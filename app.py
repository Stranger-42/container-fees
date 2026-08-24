from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام حساب رسوم الحاويات", page_icon="📦", layout="centered"
)

st.title("📦 نظام حساب رسوم الحاويات الذكي")
st.write(
    "مرحباً بك! يمكنك الاختيار بين رفع ملف إكسل جاهز أو إدخال البيانات يدوياً"
    " مباشرة من هاتفك أو حاسوبك."
)

input_method = st.radio(
    "**اختر طريقة الإدخال المناسبة لك:**",
    ("📱 💻 إدخال يدوي عبر الشاشة", "📊 رفع ملف إكسل (Excel)"),
)

containers_data = []

if input_method == "📱 💻 إدخال يدوي عبر الشاشة":
  st.markdown("---")
  num_containers = st.number_input(
      "كم عدد الحاويات التي تريد حساب رسومها؟", min_value=1, max_value=20, value=1
  )

  for i in range(num_containers):
    st.markdown(f"### 🔹 الحاوية رقم {i+1}")
    col1, col2 = st.columns(2)

    with col1:
      r_date = st.date_input(
          f"تاريخ الاستلام (حاوية {i+1})", key=f"r_{i}", value=datetime.today()
      )
      d_val = st.number_input(
          f"قيمة البيان الجمركي (دينار)",
          min_value=0.0,
          value=10000.0,
          key=f"v_{i}",
      )

    with col2:
      e_date = st.date_input(
          f"تاريخ الخروج (حاوية {i+1})", key=f"e_{i}", value=datetime.today()
      )
      t_weight = st.number_input(
          f"الوزن الإجمالي (طن)", min_value=0.0, value=25.0, key=f"w_{i}"
      )

    containers_data.append({
        "receipt_date": str(r_date),
        "exit_date": str(e_date),
        "declaration_value": d_val,
        "total_weight": t_weight,
    })
    st.markdown("---")

else:
  st.markdown("---")
  uploaded_file = st.file_uploader(
      "اختر ملف الإكسل (receipt_date, exit_date, declaration_value,"
      " total_weight)",
      type=["xlsx", "xls"],
  )

  if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    containers_data = df.to_dict(orient="records")
    st.success(
        f"تم بنجاح قراءة البيانات لعدد {len(containers_data)} حاوية من الملف."
    )

if st.button("🧮 حساب الرسوم الإجمالية", type="primary"):
  if not containers_data:
    st.warning("الرجاء إدخال البيانات أو رفع ملف إكسل أولاً.")
  else:
    grand_total = 0
    report_results = []

    for index, container in enumerate(containers_data, start=1):
      d1 = pd.to_datetime(container["receipt_date"])
      d2 = pd.to_datetime(container["exit_date"])
      storage_days = (d2 - d1).days
      if storage_days < 0:
        storage_days = 0

      storage_fee = storage_days * 15
      guard_fee = 250
      declaration_fee = container["declaration_value"] * 0.003
      weight_fee = container["total_weight"] * 1

      container_total = storage_fee + guard_fee + declaration_fee + weight_fee
      grand_total += container_total

      report_results.append({
          "الحاوية": f"رقم {index}",
          "أيام التخزين": f"{storage_days} يوم",
          "رسوم التخزين": f"{storage_fee} د",
          "بدل الحراسة": f"{guard_fee} د",
          "رسوم البيان": f"{declaration_fee:.2f} د",
          "رسوم الوزن": f"{weight_fee} د",
          "الإجمالي": f"{container_total:.2f} د",
      })

    st.success("تم إتمام الحسابات بنجاح!")
    result_df = pd.DataFrame(report_results)
    st.table(result_df)
    st.markdown(
        f"### 💰 الإجمالي الكلي للرسوم: **{grand_total:.2f} دينار**"
    )
