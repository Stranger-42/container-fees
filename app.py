from datetime import datetime
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام حساب رسوم الحاويات", page_icon="📦", layout="centered"
)

# تخصيص التصميم: الخطوط الكبيرة واللون الأزرق والتنسيق المحسن
st.markdown(
    """
    <style>
    /* تغيير لون الحجم لكل العناوين الرئيسية إلى أزرق داكن وواضح */
    h1, h2, h3 {
        color: #1e3a8a !important;
        font-family: 'Tahoma', sans-serif;
    }
    
    /* تنسيق صندوق النتيجة الكلية */
    .total-box {
        background-color: #eff6ff;
        padding: 18px;
        border-radius: 12px;
        border: 2px solid #3b82f6;
        text-align: center;
        font-size: 22px !important;
        color: #1e40af !important;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* تنسيق النصوص العادية والتعليمات */
    p, label, .stMarkdown {
        font-size: 16px !important;
        color: #334155;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📦 نظام حساب رسوم الحاويات الذكي")
st.markdown(
    "<p style='color: #475569; font-size: 16px;'>نظام احتساب الرسوم وفق"
    " التعريفة المعتمدة (تخزين 15 د/يوم، مناولة وحراسة 265 د، تأمين البيان"
    " 0.003، وخدمات عامة 1 د لكل طن).</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# الخطوة الأولى: المعلومات الأساسية ورقم المرجع
st.markdown("### 📝 الخطوة 1: المعلومات الأساسية ورقم المرجع")
col_r1, col_r2 = st.columns(2)
with col_r1:
  ref_number = st.text_input(
      "رقم المرجع (رقم الحاوية أو رقم البوليصة)", value="BOL-2026-001"
  )
with col_r2:
  shared_weight = st.number_input(
      "الوزن الإجمالي (طن)",
      min_value=0.0,
      value=None,
      step=1.0,
      placeholder="أدخل الوزن الإجمالي...",
  )

col_r3, col_r4 = st.columns(2)
with col_r3:
  shared_declaration = st.number_input(
      "قيمة البيان الجمركي (دينار)",
      min_value=0.0,
      value=None,
      step=100.0,
      format="%0.2f",
      placeholder="0.00",
  )
with col_r4:
  handling_guard_fee_per_container = st.number_input(
      "بدل مناولة وحراسة (للحاوية)", min_value=0.0, value=265.0, step=5.0
  )

# خانة إدخال البريد الإلكتروني للإرسال
recipient_email_input = st.text_input(
    "البريد الإلكتروني المراد الإرسال إليه (اختياري)",
    value="Amerbasuoni@yahoo.com",
    placeholder="example@domain.com",
)

st.markdown("---")

# الخطوة الثانية: تحديد عدد الحاويات
st.markdown("### 🔢 الخطوة 2: عدد الحاويات")
num_containers = st.number_input(
    "كم عدد الحاويات المراد حساب رسومها؟", min_value=1, max_value=20, value=1
)

st.markdown("---")

# الخطوة الثالثة: تواريخ الاستلام والخروج لكل حاوية
st.markdown("### 📅 الخطوة 3: تواريخ الحاويات (استلام وخروج)")
containers_data = []

for i in range(int(num_containers)):
  st.markdown(
      f"<h4 style='color: #2563eb;'>🔹 تفاصيل الحاوية رقم {i+1}</h4>",
      unsafe_allow_html=True,
  )
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

if st.button("🧮 حساب الرسوم", type="primary"):
  if shared_weight is None or shared_declaration is None:
    st.warning("الرجاء إدخال الوزن الإجمالي وقيمة البيان الجمركي أولاً.")
  elif not containers_data:
    st.warning("الرجاء إدخال تواريخ الحاويات أولاً.")
  else:
    num_containers_count = len(containers_data)
    total_insurance = shared_declaration * 0.003
    total_general_services = shared_weight * 1.0

    insurance_share_per_container = total_insurance / num_containers_count
    general_services_share_per_container = (
        total_general_services / num_containers_count
    )

    grand_total = 0
    report_results = []

    # تصميم نص التقرير الاحترافي للتحميل والطباعة والإرسال
    report_lines = [
        "==================================================",
        "           كشف حساب رسوم الحاويات والساحات          ",
        "==================================================",
        f"📅 تاريخ الإصدار: {datetime.today().strftime('%Y-%m-%d')}",
        f"📌 رقم المرجع (الحاوية/البوليصة): {ref_number}",
        f"⚖️ إجمالي الوزن: {shared_weight} طن",
        f"📋 قيمة البيان الجمركي: {shared_declaration:,.2f} دينار",
        f"🔢 عدد الحاويات: {num_containers_count}",
        "--------------------------------------------------",
        "              تفاصيل حساب الرسوم للحاويات            ",
        "--------------------------------------------------",
    ]

    for index, container in enumerate(containers_data, start=1):
      d1 = pd.to_datetime(container["receipt_date"])
      d2 = pd.to_datetime(container["exit_date"])
      storage_days = (d2 - d1).days
      if storage_days < 0:
        storage_days = 0

      storage_fee = storage_days * 15
      handling_guard_fee = handling_guard_fee_per_container

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
          "رسوم التخزين (15 د)": f"{storage_fee:,.2f} د",
          "مناولة وحراسة": f"{handling_guard_fee:,.2f} د",
          "تأمين البيان (حصة)": f"{insurance_share_per_container:,.2f} د",
          "خدمات عامة (حصة)": f"{general_services_share_per_container:,.2f} د",
          "الإجمالي": f"{container_total:,.2f} د",
      })

      report_lines.extend([
          f"🔹 الحاوية رقم ({index}):",
          f"   • فترة التخزين: {storage_days} أيام (رسوم التخزين: {storage_fee:,.2f} د)",
          f"   • بدل مناولة وحراسة: {handling_guard_fee:,.2f} د",
          f"   • حصة تأمين البيان: {insurance_share_per_container:,.2f} د",
          f"   • حصة الخدمات العامة: {general_services_share_per_container:,.2f} د",
          f"   ➔ إجمالي الحاوية ({index}): {container_total:,.2f} دينار",
          "--------------------------------------------------",
      ])

    report_lines.extend([
        "==================================================",
        f"💰 الإجمالي الكلي للرسوم: {grand_total:,.2f} دينار",
        "==================================================",
        "⚠️ ملاحظة: هذا التقرير لغاية الاحتساب وليس وثيقة رسمية نهائية.",
        "🛠️ إعداد وتطوير: السيد علي بسيوني",
        "==================================================",
    ])

    full_report_text = "\n".join(report_lines)

    st.success("تم إتمام الحسابات بنجاح!")
    st.info(
        f"📌 **رقم المرجع:** {ref_number} | **تأمين البيان الكلي:**"
        f" {total_insurance:,.2f} د | **خدمات عامة الكلية:**"
        f" {total_general_services:,.2f} د"
    )

    result_df = pd.DataFrame(report_results)
    st.table(result_df)

    # عرض الإجمالي الكلي بصندوق أزرق كبير وبارز
    st.markdown(
        f"""
        <div class="total-box">
            💰 الإجمالي الكلي للرسوم: {grand_total:,.2f} دينار
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state["last_report"] = full_report_text
    st.session_state["ref_number"] = ref_number
    st.session_state["extra_email"] = (
        recipient_email_input
        if recipient_email_input
        else "Amerbasuoni@yahoo.com"
    )

if "last_report" in st.session_state:
  st.markdown("---")
  st.markdown(
      "<h3 style='color: #1e3a8a;'>🖨️ 📧 خيارات التحميل، الإرسال، والطباعة</h3>",
      unsafe_allow_html=True,
  )

  # تجهيز رابط الـ mailto الآمن لفتح تطبيق الإيميل مباشرة مع البيانات
  encoded_subject = urllib.parse.quote(
      f"كشف حساب رسوم حاويات - رقم المرجع: {st.session_state['ref_number']}"
  )
  encoded_body = urllib.parse.quote(st.session_state["last_report"])
  mailto_link = f"mailto:{st.session_state['extra_email']}?subject={encoded_subject}&body={encoded_body}"

  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    st.download_button(
        label="📥 تحميل التقرير (.txt)",
        data=st.session_state["last_report"].encode("utf-8-sig"),
        file_name=f"Container_Fees_{st.session_state['ref_number']}.txt",
        mime="text/plain;charset=utf-8",
    )
  with col_p2:
    st.markdown(
        f"""
        <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
            <div style="width: 100%; background-color: #2563eb; color: white; padding: 11px 10px; border-radius: 6px; font-weight: bold; text-align: center; font-family: Tahoma; font-size: 15px;">
                📤 إرسال عبر البريد
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
  with col_p3:
    st.markdown(
        """
        <button onclick="window.print()" style="width: 100%; background-color: #2563eb; color: white; padding: 11px 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-family: Tahoma; font-size: 15px;">
            🖨️ طباعة الفاتورة
        </button>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 14px;'>"
    "<b>⚠️ ملاحظة:</b> هذا البرنامج لغاية الاحتساب وليس رسمياً<br>"
    "تم إنشاء هذا البرنامج من خلال <b>السيد علي بسيوني</b>"
    "</div>",
    unsafe_allow_html=True,
)

