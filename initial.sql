-- Create the account_type table
CREATE TABLE account_type (
  type_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  account_type_name NVARCHAR2(50) NOT NULL
);

-- Insert the account types
INSERT INTO account_type (account_type_name) VALUES ('Qu?n Tr? Vi�n');
INSERT INTO account_type (account_type_name) VALUES ('Gi�o Vi�n');
INSERT INTO account_type (account_type_name) VALUES ('Ph? Huynh');
INSERT INTO account_type (account_type_name) VALUES ('H?c Sinh');

-- Create the School table
CREATE TABLE school (
  school_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  school_name NVARCHAR2(100) NOT NULL,
  address NVARCHAR2(200) NOT NULL,
  phone_number NVARCHAR2(20) NOT NULL,
  email NVARCHAR2(100),
  description CLOB,
  school_logo NVARCHAR2(100)
);

INSERT INTO school (school_name, address, phone_number, email, description, school_logo) VALUES
  ('Tr??ng THPT Marie Curie', '159 ?. Nam K? Kh?i Ngh?a, V� Th? S�u, Qu?n 3, Th�nh ph? H? Ch� Minh', ' 028 3930 6850', NULL, NULL, NULL);

-- Create the class table
CREATE TABLE class(
  class_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  class_academic_year NUMBER NOT NULL,
  class_grade NUMBER NOT NULL,
  class_character NVARCHAR2(1) NOT NULL,
  class_sequence NUMBER NOT NULL,
  class_teacher_id NUMBER
);

-- Create the Users table
CREATE TABLE users (
  user_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  type_id NUMBER NOT NULL,
  gender NUMBER,
  date_of_birth DATE,
  first_name NVARCHAR2(100),
  last_name NVARCHAR2(100),
  user_name NVARCHAR2(100) UNIQUE NOT NULL,
  password NVARCHAR2(100),
  phone_number NVARCHAR2(20),
  email NVARCHAR2(100) UNIQUE NOT NULL,
  address NVARCHAR2(200),
  school_id NUMBER,
  class_id NUMBER,
  occupation NVARCHAR2(100),
  description CLOB,
  student_parent_id NUMBER,
  FOREIGN KEY (type_id) REFERENCES account_type (type_id),
  FOREIGN KEY (school_id) REFERENCES school (school_id),
  FOREIGN KEY (class_id) REFERENCES class (class_id)
);

ALTER TABLE class ADD FOREIGN KEY (class_teacher_id) REFERENCES users (user_id);
ALTER TABLE users ADD FOREIGN KEY (student_parent_id) REFERENCES users (user_id);

-- Create the Course table
CREATE TABLE course (
  course_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  course_name NVARCHAR2(100) NOT NULL,
  time_start_in_day TIMESTAMP NOT NULL,
  time_end_in_day TIMESTAMP NOT NULL,
  day_of_week NUMBER NOT NULL,
  course_teacher_id NUMBER NOT NULL,
  course_academic_year NUMBER NOT NULL,
  course_semester NUMBER NOT NULL,
  FOREIGN KEY (course_teacher_id) REFERENCES users (user_id)
);

-- Create the Deadline table
CREATE TABLE deadline (
  deadline_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_start DATE NOT NULL,
  date_end DATE NOT NULL,
  from_course_id NUMBER,
  by_teacher_id NUMBER,
  title NVARCHAR2(100) NOT NULL,
  description CLOB,
  FOREIGN KEY (from_course_id) REFERENCES course (course_id),
  FOREIGN KEY (by_teacher_id) REFERENCES users (user_id)
);

CREATE TABLE grade_detail (
  grade_detail_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  grade_detail_name NVARCHAR2(100) NOT NULL,
  grade_detail_coefficient FLOAT NOT NULL,
  grade_point FLOAT NOT NULL,
  grade_detail_description CLOB,
  grade_detail_course_id NUMBER,
  FOREIGN KEY (grade_detail_course_id) REFERENCES course (course_id)
);

-- Create the deadline_student table
CREATE TABLE deadline_student (
  deadline_id NUMBER,
  student_id NUMBER,
  deadline_student_status NUMBER DEFAULT 1,
  deadline_student_answer CLOB NOT NULL,
  grade_detail_course_id NUMBER,
  PRIMARY KEY (deadline_id, student_id),
  FOREIGN KEY (deadline_id) REFERENCES deadline (deadline_id),
  FOREIGN KEY (student_id) REFERENCES users (user_id),
  FOREIGN KEY (grade_detail_course_id) REFERENCES grade_detail (grade_detail_id)
);

CREATE TABLE student_time_off (
  student_id NUMBER,
  time_off_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  time_off_date DATE NOT NULL,
  time_off_session NUMBER NOT NULL,
  time_off_reason CLOB NOT NULL,
  time_off_status NUMBER DEFAULT 1,
  FOREIGN KEY (student_id) REFERENCES users (user_id)
);

CREATE TABLE annoucement (
  annoucement_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  annoucement_student_id NUMBER,
  annoucement_title NVARCHAR2(100) NOT NULL,
  annoucement_content CLOB,
  annoucement_datetime TIMESTAMP NOT NULL,
  FOREIGN KEY (annoucement_student_id) REFERENCES users (user_id)
);

CREATE TABLE user_password_reset (
  user_id NUMBER,
  password_reset_hashed_token NVARCHAR2(120) NOT NULL,
  password_reset_expiration TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (user_id),
  PRIMARY KEY (user_id)
);

CREATE OR REPLACE FUNCTION get_date_plus_x_minutes(x IN NUMBER) RETURN TIMESTAMP IS
  v_current_date TIMESTAMP;
BEGIN
  v_current_date := SYSTIMESTAMP + INTERVAL '1' MINUTE * x;
  RETURN v_current_date;
END;

CREATE OR REPLACE TRIGGER tr_set_password_reset_expiration_user_password_reset
BEFORE INSERT ON user_password_reset
FOR EACH ROW
BEGIN
  :NEW.password_reset_expiration := get_date_plus_x_minutes(5);
END;
/

--INSERT INTO user_password_reset (user_id, password_reset_hashed_token) VALUES (3, '12345');

-- Create the trigger to delete expired password reset token every 5 minutes
BEGIN 
  DBMS_SCHEDULER.CREATE_JOB(
    job_name => 'DELETE_EXPIRED_PASSWORD_RESET_TOKEN',
    job_type => 'PLSQL_BLOCK',
    job_action => 'BEGIN DELETE FROM user_password_reset WHERE password_reset_expiration < SYSTIMESTAMP; END;',
    start_date => SYSTIMESTAMP,
    repeat_interval => 'FREQ=MINUTELY; INTERVAL=5',
    enabled => TRUE
  );
END;
/