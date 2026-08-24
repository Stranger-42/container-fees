from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام حساب رسوم الحاويات", page_icon="📦", layout="centered"
)

st.title("📦 نظام حساب رسوم الحاويات الذكي")
st.write(
    "مرحباً بك! نظام حساب الرسوم وفق التعريفة المعتمدة (تخزين 15 د/يوم لكل حاوية"
    " ، مناولة وحراسة 265 د لكل حاوية، تأمين البيان 0.003، وخدمات عامة 1 د لكل"
    " طن)."
)

# القيم الموحدة للجميع (تظهر دائماً)
st.markdown("### ⚙️ القيم المشتركة للشحنة")
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
  shared_weight = st.number_input(
      "الوزن الإجمالي (طن)", min_value=0.0, value=25.0, step=1.0
  )
with col_g2:
  shared_declaration = st.number_input(
      "قيمة البيان الجمركي (دينار)", min_value=0.0, value=10000.0, step=100.0
  )
with col_g3:
  handling_guard_fee_per_container = st.number_input(
      "بدل مناولة وحراسة (للحاوية)", min_value=0.0, value=265.0, step=5.0
  )

st.markdown("---")

input_method = st.radio(
    "**اختر طريقة الإدخال المناسبة لك:**",
    ("📱 💻 إدخال يدوي عبر الشاشة", "📊 رفع ملف إكسل (Excel)"),
)

containers_data = []

if input_method == "📱 💻 إدخال يدوي عبر الشاشة":
  num_containers = st.number_input(
      "كم عدد الحاويات التي تريد حساب رسومها؟", min_value=1, max_value=20, value=1
  )

  st.markdown("### 📅 تواريخ الحاويات")
  for i in range(num_containers):
    st.markdown(f"#### 🔹 الحاوية رقم {i+1}")
    col1, col2 = st.columns(2)

    with col1:
      r_date = st.date_input(
          f"تاريخ الاستلام (حاوية {i+1})", key=f"r_{i}", value=datetime.today()
      )

    with col2:
      e_date = st.date_input(
          f"تاريخ الخروج (حاوية {i+1})", key=f"e_{i}", value=datetime.today()
      )

    containers_data.append({
        "receipt_date": str(r_date),
        "exit_date": str(e_date),
    })
    st.markdown("---")

else:
  uploaded_file = st.file_uploader(
      "اختر ملف الإكسل (يجب أن يحتوي على أعمدة: receipt_date, exit_date)",
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
    st.warning("الرجاء إدخال تواريخ الحاويات أو رفع ملف إكسل أولاً.")
  else:
    num_containers_count = len(containers_data)

    # الرسوم الإجمالية الثابتة للبيان (بغض النظر عن عدد الحاويات)
    total_insurance = shared_declaration * 0.003
    total_general_services = shared_weight * 1.0

    # حصة كل حاوية من الرسوم الثابتة لتوزيعها في الجدول
    insurance_share_per_container = total_insurance / num_containers_count
    general_services_share_per_container = (
        total_general_services / num_containers_count
    )

    grand_total = 0
    report_results = []

    for index, container in enumerate(containers_data, start=1):
      d1 = pd.to_datetime(container["receipt_date"])
      d2 = pd.to_datetime(container["exit_date"])
      storage_days = (d2 - d1).days
      if storage_days < 0:
        storage_days = 0

      storage_fee = storage_days * 15  # 15 دينار لكل يوم لكل حاوية
      handling_guard_fee = handling_guard_fee_per_container  # 265 لكل حاوية

      # مجموع رسوم هذه الحاوية
      container_total = (
          storage_fee
          + handling_guard_fee
          + insurance_share_per_container
          + general_services_share_per_container
      )
      grand_total += container_total

      report_results.append({
          "الحاوية": f"رقم {index}",
          "أيام التخزين": f"{storage_days} يوم",
          "رسوم التخزين (15 د)": f"{storage_fee:.2f} د",
          "مناولة وحراسة": f"{handling_guard_fee:.2f} د",
          "تأمين البيان (حصة)": f"{insurance_share_per_container:.2f} د",
          "خدمات عامة (حصة)": f"{general_services_share_per_container:.2f} د",
          "الإجمالي": f"{container_total:.2f} د",
      })

    st.success("تم إتمام الحسابات بنجاح وفق التعريفة المعتمدة!")

    # عرض ملخص إضافي للرسوم الثابتة
    st.info(
        f"📌 **ملخص الرسوم الثابتة للشحنة:** تأمين البيان الكلي ="
        f" {total_insurance:.2f} د | خدمات عامة الكلية ="
        f" {total_general_services:.2f} د"
    )

    result_df = pd.DataFrame(report_results)
    st.table(result_df)
    st.markdown(
        f"### 💰 الإجمالي الكلي للرسوم: **{grand_total:.2f} دينار**"
    )

# التوقيع والملاحظة الرسمية في الأسفل
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 13px;'>"
    "<b>⚠️ ملاحظة:</b> هذا البرنامج لغاية الاحتساب وليس رسمياً<br>"
    "تم إنشاء هذا البرنامج من خلال <b>السيد علي بسيوني</b>"
    "</div>",
    unsafe_allow_html=True,
)
