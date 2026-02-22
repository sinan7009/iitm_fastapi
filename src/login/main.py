from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from save_data import get_all_json_data
from db_setup import create_dashboard_table, insert_course_data
from src.speak.speak import get_intent_response
from datetime import datetime

class IITMPortal:
    def __init__(self, driver_path="chromedriver.exe"):
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.login()

    def login(self):
        self.driver.get("https://ds.study.iitm.ac.in/student_dashboard/")
        print("🔑 Please log in manually...")
        get_intent_response("login_request")

        try:
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.ID, "credits-earned"))
            )
            print("✅ Login detected!")
            get_intent_response("login_success")


            self.credit_earned()
        except Exception as e:
            get_intent_response("login_failed")
            print("⚠️ Error in login:", e)

    def credit_earned(self):
        WebDriverWait(self.driver, 60).until(
            EC.text_to_be_present_in_element((By.ID, "credits-earned"), "")
        )
        credits_earned = self.driver.find_element(By.ID, "credits-earned").text
        credits_pursued = self.driver.find_element(By.ID, "credits-pursued").text
        print(f"📘 Credits Earned: {credits_earned}")
        print(f"📗 Credits Pursued: {credits_pursued}")
        self.exam_date()

    def exam_date(self):
        self.driver.get("https://ds.study.iitm.ac.in/student_dashboard/exam_cities_and_hall_ticket")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
        )

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        print("\n🧾 Exam Schedule:")
        exam_details = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                exam_name = cols[0].text.strip()
                exam_details.append({
                    "name": cols[0].text.strip(),
                    "date": cols[1].text.strip(),
                    "told": False
                })

        self.cgpa_and_assignment(exam_details)

    def cgpa_and_assignment(self, exam_details):
        self.driver.get("https://ds.study.iitm.ac.in/student_dashboard/current_courses")
        cgpa_element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Cumulative Grade Point Average')]/span")
            )
        )
        cgpa = {"cgpa": cgpa_element.text.strip()}
        print(f"🎓 CGPA: {cgpa}")
        print(exam_details)
        a = get_all_json_data(exam_details, cgpa)
        print(a)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".courses-box"))
        )

        self.link_dict = {}
        courses = self.driver.find_elements(By.CSS_SELECTOR, ".courses-box")

        assignments = {}

        for course in courses:
            title = course.find_element(By.CSS_SELECTOR, ".courses-thumbnail-text").text.strip()
            link = course.find_element(By.TAG_NAME, "a").get_attribute("href")
            self.link_dict[title] = link

            print(f"\n📘 {title}\n🔗 {link}")

            for a in course.find_elements(By.CSS_SELECTOR, "p.assignment-text"):
                text = a.text.strip()
                if " - " in text:
                    name, mark = text.rsplit(" - ", 1)
                    if title not in assignments:
                        assignments[title] = []
                    assignments[title].append({
                        "title": name,
                        "mark": mark,
                        "told": False
                    })

            print(assignments)
        print("\n🖱️ You can now click any course card manually to open it (in new tab).")
        get_intent_response("fetch_complete")
        create_dashboard_table(assignments)
        get_intent_response("cgpa_announcement", cgpa=cgpa_element.text.strip())

        for exam in exam_details:
            exam["date_obj"] = datetime.strptime(exam["date"], "%d %B %Y")  # e.g., "12 November 2025"
            print("your exam date",exam["date_obj"])
        # Find upcoming exams
        now = datetime.now()
        print("today ", now)
        upcoming_exams = [exam for exam in exam_details if exam["date_obj"] >= now]
        print(upcoming_exams)

        if upcoming_exams:
            next_exam = sorted(upcoming_exams, key=lambda x: x["date_obj"])[0]
            days_left = (next_exam["date_obj"] - now).days
            print(days_left)
            print("Next exam:", next_exam)

            # Speak dynamically

            if days_left <= 20:
                get_intent_response(
                    "upcoming_exam_soon",
                    exam_name=next_exam["name"],
                    exam_date=next_exam["date"],
                    days_left=days_left
                )
            else:
                get_intent_response(
                    "next_exam",
                    exam_name=next_exam["name"],
                    exam_date=next_exam["date"],
                    days_left=days_left
                )
        else:
            print("No upcoming exams.")

        # self.wait_for_new_tab()

        self.wait_for_new_tab()

    def wait_for_new_tab(self):
        print("⏳ Waiting for a new tab to open after you click a course...")

        original_tabs = self.driver.window_handles
        while True:
            current_tabs = self.driver.window_handles
            if len(current_tabs) > len(original_tabs):
                new_tab = [t for t in current_tabs if t not in original_tabs][0]
                self.driver.switch_to.window(new_tab)
                print(f"🌐 Switched to new tab: {self.driver.current_url}")

                if "seek.onlinedegree.iitm.ac.in/courses" in self.driver.current_url:
                    self.current_course(self.driver.current_url)

    def current_course(self, c_link):
        print("📖 Scraping course content...")
        self.driver.get(c_link)

        # Wait for week buttons
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.units__items-text"))
        )
        week_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.units__items-text")
        title_elem = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.course-title"))
        )
        full_title = title_elem.text.strip()
        course_name = full_title.split(" - ")[-1].strip()  # ✅ gets only 'Python'
        print(course_name)
        print("\n📚 Course Weeks Found:")
        course_data = {
            "name": course_name,
            "link": c_link,
            "weeks": []
        }

        for i, btn in enumerate(week_buttons, 1):
            try:
                # Get week title
                week_title = btn.find_element(By.CSS_SELECTOR, ".units__items-title").text.strip()
                print(f"\n  ➤ {i}. {week_title}")

                # Scroll and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)

                # Find all subitems (contents)
                subitems = self.driver.find_elements(By.CSS_SELECTOR, ".units__subitems-text")

                # Week dictionary
                week_data = {
                    "week_number": i,
                    "week_title": week_title,
                    "contents": []
                }

                for sub in subitems:
                    try:
                        title_elem = sub.find_element(By.CSS_SELECTOR, ".units__subitems-title span")
                        title = title_elem.text.strip()
                        if not title:
                            continue
                    except:
                        continue

                    # Detect content type (Video, Assignment, etc.)
                    try:
                        type_ = sub.find_element(By.CSS_SELECTOR, ".units__subitems-videos").text.strip()
                    except:
                        type_ = "Unknown"

                    # Determine if graded or submitted
                    is_graded = "Graded Assignment" in title or "Programming Assignment" in title
                    submitted = bool(sub.find_elements(By.CSS_SELECTOR, ".submitted-icon"))
                    mark = "yes" if submitted else "no" if is_graded else ""

                    week_data["contents"].append({
                        "title": title,
                        "type": type_,
                        "graded": is_graded,
                        "submitted": submitted,
                        "mark": mark
                    })

                    # Print summary
                    if is_graded:
                        print(f"     🧾 {title} — {type_} {mark}")
                    else:
                        print(f"     🔹 {title} — {type_}")

                # Add week to course
                course_data["weeks"].append(week_data)

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️ Error reading week {i}: {e}")
                continue
        print("\n✅ Finished scraping visible week data.")
        print("\n📦 Final Course Data:\n", course_data)
        insert_course_data(course_data)
        self.wait_for_new_tab()



if __name__ == "__main__":
    IITMPortal()
