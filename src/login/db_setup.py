import psycopg2
from datetime import date


def get_connection():
    return psycopg2.connect(
        dbname="iitm_dashboard",
        user="postgres",        # default username
        password="qwerty00",
        host="localhost",
        port="5432"
    )


def create_dashboard_table(assign):
    conn = get_connection()
    cur = conn.cursor()
    for subject in assign:
        table_name = subject.replace(" ", "_").lower()
        create_script = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                id SERIAL PRIMARY KEY,
                update_date DATE DEFAULT CURRENT_DATE,
                title TEXT,
                mark TEXT,
                told BOOLEAN DEFAULT FALSE
            );
        '''
        cur.execute(create_script)
        conn.commit()
        print(f"✅ Table '{table_name}' created successfully!")

        cur.execute(f'SELECT title FROM "{table_name}";')
        existing_titles = {row[0] for row in cur.fetchall()}

        for data in assign[subject]:
            title = data['title']
            mark = data['mark']
            if title not in existing_titles:
                insert_script = f'''
                                    INSERT INTO "{table_name}" (title, mark)
                                    VALUES (%s, %s);
                                '''
                insert_value = (title,mark)
                cur.execute(insert_script, insert_value)
                conn.commit()
                print("values inserted sucessfully")
            else:
                print("data allready exist")


def create_course_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            link TEXT,
            last_update_date DATE DEFAULT CURRENT_DATE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS weeks (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
            week_number INTEGER,
            week_title TEXT
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS contents (
            id SERIAL PRIMARY KEY,
            week_id INTEGER REFERENCES weeks(id) ON DELETE CASCADE,
            title TEXT,
            type TEXT,
            graded BOOLEAN DEFAULT FALSE,
            submitted BOOLEAN DEFAULT FALSE,
            mark TEXT
        );
    ''')

    conn.commit()
    conn.close()
    print("✅ Course tables created successfully!")


def insert_course_data(course_data):
    conn = get_connection()
    cur = conn.cursor()

    # Insert or update course
    cur.execute('''
        INSERT INTO courses (name, link, last_update_date)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET last_update_date = EXCLUDED.last_update_date
        RETURNING id;
    ''', (course_data["name"], course_data["link"], date.today()))
    course_id = cur.fetchone()[0]

    for week in course_data["weeks"]:
        cur.execute('''
            INSERT INTO weeks (course_id, week_number, week_title)
            VALUES (%s, %s, %s)
            RETURNING id;
        ''', (course_id, week["week_number"], week["week_title"]))
        week_id = cur.fetchone()[0]

        for content in week["contents"]:
            cur.execute('''
                INSERT INTO contents (week_id, title, type, graded, submitted, mark)
                VALUES (%s, %s, %s, %s, %s, %s);
            ''', (
                week_id,
                content["title"],
                content["type"],
                content["graded"],
                content["submitted"],
                content["mark"]
            ))

    conn.commit()
    conn.close()
    print(f"✅ Data inserted for course: {course_data['name']}")