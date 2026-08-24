from datetime import datetime
import email.mime.multipart
import email.mime.text
import smtplib
import ssl
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام حساب رسوم الحاويات", page_icon="📦", layout="centered"
)

st.title("📦 نظام حساب رسوم الحاويات الذكي")
st.write(
    "نظام احتساب الرسوم وفق التعريفة المعتمدة (تخزين 15 د/يوم، مناولة وحراسة"
    " 265 د، تأمين البيان 0.003، وخدمات عامة 1 د لكل طن)."
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
      "الوزن الإجمالي (طن)", min_value=0.0, value=25.0, step=1.0
  )

col_r3, col_r4 = st.columns(2)
with col_r3:
  shared_declaration = st.number_input(
      "قيمة البيان الجمركي (دينار)", min_value=0.0, value=10000.0, step=100.0
  )
with col_r4:
  handling_guard_fee_per_container = st.number_input(
      "بدل مناولة وحراسة (للحاوية)", min_value=0.0, value=265.0, step=5.0
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
  st.markdown(f"#### 🔹 تفاصيل الحاوية رقم {i+1}")
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


# وظيفة إرسال البريد الإلكتروني
def send_email_report(report_text, ref_no):
  try:
    sender_email = st.secrets["email"]["sender_email"]
    sender_password = st.secrets["email"]["sender_password"]
  except Exception:
    return (
        False,
        "لم يتم ضبط إعدادات البريد الإلكتروني في إعدادات المنصة (Secrets).",
    )

  receiver_email = "Amerbasuoni@yahoo.com"

  message = email.mime.multipart.MIMEMultipart("alternative")
  message["Subject"] = f"كشف حساب رسوم حاويات - رقم المرجع: {ref_no}"
  message["From"] = sender_email
  message["To"] = receiver_email

  part = email.mime.text.MIMEText(report_text, "plain", "utf-8")
  message.attach(part)

  try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, receiver_email, message.as_string())
    return True, "تم إرسال التقرير بنجاح إلى البريد الإلكتروني."
  except Exception as e:
    return False, f"فشل في إرسال البريد الإلكتروني: {e}"


if st.button("🧮 حساب الرسوم وإرسال التقرير", type="primary"):
  if not containers_data:
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
    email_body_lines = [
        "تقرير حساب رسوم الحاويات والساحات",
        f"رقم المرجع (الحاوية/البوليصة): {ref_number}",
        f"إجمالي الوزن: {shared_weight} طن",
        f"قيمة البيان الجمركي: {shared_declaration} دينار",
        f"عدد الحاويات: {num_containers_count}",
        "-" * 30,
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
          "رسوم التخزين (15 د)": f"{storage_fee:.2f} د",
          "مناولة وحراسة": f"{handling_guard_fee:.2f} د",
          "تأمين البيان (حصة)": f"{insurance_share_per_container:.2f} د",
          "خدمات عامة (حصة)": f"{general_services_share_per_container:.2f} د",
          "الإجمالي": f"{container_total:.2f} د",
      })

      email_body_lines.append(
          f"الحاوية {index}: تخزين {storage_days} أيام ({storage_fee}د) |"
          f" الإجمالي: {container_total:.2f} د"
      )

    email_body_lines.append("-" * 30)
    email_body_lines.append(f"الإجمالي الكلي للرسوم: {grand_total:.2f} دينار")
    email_body_lines.append(
        "\nملاحظة: هذا البرنامج لغاية الاحتساب وليس رسمياً."
    )
    email_body_lines.append("إعداد: السيد علي بسيوني")

    full_email_text = "\n".join(email_body_lines)

    st.success("تم إتمام الحسابات بنجاح!")

    st.info(
        f"📌 **رقم المرجع:** {ref_number} | **تأمين البيان الكلي:**"
        f" {total_insurance:.2f} د | **خدمات عامة الكلية:**"
        f" {total_general_services:.2f} د"
    )

    result_df = pd.DataFrame(report_results)
    st.table(result_df)
    st.markdown(
        f"### 💰 الإجمالي الكلي للرسوم: **{grand_total:.2f} دينار**"
    )

    # إرسال الإيميل
    email_success, email_msg = send_email_report(full_email_text, ref_number)
    if email_success:
      st.success(email_msg)
    else:
      st.warning(
          f"{email_msg} (ملاحظة: لإرسال البريد فعلياً، تأكد من إعداد Secrets"
          " في لوحة تحكم Streamlit)"
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
