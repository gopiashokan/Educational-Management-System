import os
import cv2
import time
import numpy as np
import pandas as pd
import psycopg2
import bcrypt
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
from dotenv import load_dotenv
from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tensorflow.keras.models import load_model
import warnings

warnings.filterwarnings('ignore')
load_dotenv()


def streamlit_config():
    # page configuration
    st.set_page_config(page_title='EMS', page_icon='book', layout="wide")

    # page header transparent color
    page_background_color = """
    <style>

    [data-testid="stHeader"] 
    {
    background: rgba(0,0,0,0);
    }

    </style>
    """
    st.markdown(page_background_color, unsafe_allow_html=True)

    # title and position
    st.markdown(f'<h1 style="text-align: center;">EDUCATIONAL MANAGEMENT SYSTEM</h1>',
                unsafe_allow_html=True)
    add_vertical_space(4)



class sql:

    def create_database():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DEFAULT_DATABASE'))

            connection.autocommit = True
            cursor = connection.cursor()

            # create a new database
            cursor.execute(f"create database {os.getenv('DATABASE')};")

        # If database already exist means skip the process
        except psycopg2.errors.DuplicateDatabase:
            pass

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def create_login_credentials_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists login_credentials(
                                    user_id         varchar(255) not null,
                                    password        varchar(255) not null,
                                    role		    varchar(255) not null,
                                    primary key (user_id, role));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def encode_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        encode = hashed_password.decode('utf-8')
        return encode


    def add_user_login_credentials_table(user_id, password, role):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            # Encode the password
            hashed_password = sql.encode_password(password)

            # Migrate the Data to SQL Table
            cursor.execute(f'''insert into login_credentials(user_id, password, role) 
                               values('{user_id}', '{hashed_password}', '{role}');''')
            connection.commit()

            if user_id != 'admin_1' and role != 'admin':
                st.markdown(f'<h5 style="color: green;">New User Added Successfully</h5>', unsafe_allow_html=True)
                # Trigger a rerun to Refresh the Page
                st.experimental_rerun()

        except psycopg2.errors.UniqueViolation as e:
            if user_id == 'admin' and role == 'admin':
                pass
            else:
                add_vertical_space(2)
                st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def add_multiple_user_login_credentials_table(df):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.executemany(f'''insert into login_credentials(user_id, password, role) 
                               values(%s,%s,%s);''', df.values.tolist())
            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def update_user_login_credentials_table(user_id, password, role):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            # Encode the password
            hashed_password = sql.encode_password(password)

            # Migrate the Data to SQL Table
            cursor.execute(f'''update login_credentials
                               set password='{hashed_password}', role='{role}'
                               where user_id='{user_id}';''')
            connection.commit()

            st.markdown(f'<h5 style="color: green;">User Details Updated Successfully</h5>', unsafe_allow_html=True)
            # Trigger a rerun to Refresh the Page
            st.experimental_rerun()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def delete_user_login_credentials_table(user_id, role):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''delete from login_credentials
                               where user_id='{user_id}' and role='{role}';''')
            connection.commit()

            st.markdown(f'<h5 style="color: green;">User Details Deleted Successfully</h5>', unsafe_allow_html=True)
            # Trigger a rerun to Refresh the Page
            st.experimental_rerun()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def login_credentials_verification(user_id, password, role):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select password from login_credentials
                            where user_id='{user_id}' and role like '{role}%';''')
            result = cursor.fetchall()

            # Encoded Password retrieved from SQL Table
            hashed_password = result[0][0]

            # Verify the User Input Password is Matched with Encoded Hashed Password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                with st.spinner('Logging in...'):
                    time.sleep(2)
                    st.markdown(f'<h5 style="color: green;">LogIn Successfully</h5>', unsafe_allow_html=True)
                return 'LogIn Successfully'

            else:
                st.markdown(f'<h5 style="color: orange;">Password is incorrect</h5>', unsafe_allow_html=True)
                return 'Password is incorrect'

        except IndexError:
            st.markdown(f'<h5 style="color: orange;">User ID or Password is incorrect</h5>', unsafe_allow_html=True)
            return 'User Id or Password is incorrect'

        except Exception as e:
            st.markdown(f'<h5 style="color: orange;">Error: {e}</h5>', unsafe_allow_html=True)
            return e

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def create_test_qa_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists test_qa(
                                    test_id         varchar(255) not null,
                                    concept         varchar(255) not null,
                                    question_no     varchar(255) not null,
                                    question        varchar(255) not null,
                                    option_a        varchar(255) not null,
                                    option_b        varchar(255) not null,
                                    option_c        varchar(255) not null,
                                    option_d        varchar(255) not null,
                                    answer          varchar(255) not null,
                                    primary key(test_id, question_no));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_test_qa_table(df):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.executemany(f'''insert into test_qa(test_id, concept, question_no, question, 
                                                       option_a, option_b, option_c, option_d, answer) 
                                   values(%s,%s,%s,%s,%s,%s,%s,%s,%s);''', df.values.tolist())
            connection.commit()

            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align:center; color:green;">Test QA Added Successfully</h5>',
                        unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<h5 style="color: orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            if connection:
                cursor.close()
                connection.close()


    def create_student_test_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists student_test(
                                    student_id      varchar(255) not null,
                                    test_id         varchar(255) not null,
                                    concept         varchar(255) not null,
                                    question_no     int,
                                    question	    text not null,
                                    answer          text not null,
                                    mark            int,
                                    primary key (student_id, test_id, concept, question_no));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_student_test_table(df):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.executemany(f'''insert into student_test(student_id, test_id, concept, question_no, question, answer, mark) 
                                   values(%s,%s,%s,%s,%s,%s,%s);''', df.values.tolist())
            connection.commit()

            # Finally clear the data from session state
            st.session_state.test_data = {'student_id': [], 'test_id': [], 'question_no': [],
                                          'concept': [], 'question': [], 'answer': [], 'mark': []}

            st.markdown(f'<h5 style="color: green;">Test completed! Your responses have been submitted</h5>',
                        unsafe_allow_html=True)
            # Trigger a rerun to Refresh the Page
            st.experimental_rerun()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def create_student_exam_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists student_exam(
                                    student_id      varchar(255) not null,
                                    exam_id         varchar(255) not null,
                                    concept         varchar(255) not null,
                                    question_no     int not null,
                                    mark            int not null,
                                    evaluator_id    varchar(255) not null,
                                    primary key (student_id, exam_id, concept, question_no, evaluator_id));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def user_id():

        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select distinct user_id from login_credentials
                           order by user_id;''')

        result = cursor.fetchall()

        user_id = [i[0] for i in result]

        return user_id


    def create_status_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists status(
                                    identifier      varchar(255) primary key,
                                    status          varchar(255));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def delete_exam_marks_status_table(identifier, status):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''delete from status
                               where identifier='{identifier}';''')
            connection.commit()

        except psycopg2.errors.UniqueViolation as e:
            if identifier == 'upload_portal' and status == 'close':
                pass
            else:
                add_vertical_space(2)
                st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_status_table(identifier, status):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''insert into status(identifier, status) 
                               values('{identifier}', '{status}');''')
            connection.commit()

        except psycopg2.errors.UniqueViolation as e:
            if identifier == 'upload_portal' and status == 'close':
                pass
            else:
                add_vertical_space(2)
                st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def create_student_marks_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))

            cursor = connection.cursor()

            cursor.execute(f'''create table if not exists student_marks(
                                    student_id      varchar(255) not null,
                                    exam_id         varchar(255) not null,
                                    concept         varchar(255) not null,
                                    question_no     int   not null,
                                    mark            float not null,
                                    primary key (student_id, exam_id, concept, question_no));''')

            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def main():

        sql.create_database()
        sql.create_login_credentials_table()
        sql.create_student_test_table()
        sql.create_student_exam_table()
        sql.create_test_qa_table()
        sql.create_status_table()
        sql.create_student_marks_table()
        sql.add_user_login_credentials_table(user_id='admin', password='admin', role='admin')
        sql.migrate_status_table(identifier='upload_portal', status='close')



class admin:

    def account_login(role):

        col1, col2, col3, col4 = st.columns([0.1, 0.4, 0.4, 0.1], gap='medium')

        with col2:
            user_id = st.text_input(label='User ID')

        with col3:
            password = st.text_input(label='Password', type='password')

        if user_id == '' and password == '':

            add_vertical_space(1)
            col1, col2, col3, col4 = st.columns([0.1, 0.4, 0.4, 0.1], gap='medium')

            with col2:
                st.markdown(f'<h5 style="color: orange;">Please Enter User ID and Password</h5>',
                            unsafe_allow_html=True)


        elif user_id != '' and password != '':

            add_vertical_space(1)
            col1, col2, col3, col4 = st.columns([0.1, 0.4, 0.4, 0.1], gap='medium')

            with col2:
                status = sql.login_credentials_verification(user_id, password, role)

            return user_id, status


    def view_user():
        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select user_id, role from login_credentials
                           order by user_id;''')
        result = cursor.fetchall()

        index = [i for i in range(1, len(result) + 1)]
        columns = [i[0] for i in cursor.description]

        df = pd.DataFrame(result, columns=columns, index=index)
        df = df.rename_axis('s.no')
        df = pd.DataFrame(df)
        st.dataframe(df)


    def add_user():
        
        add_vertical_space(1)
        try:
            with st.form('Add User'):
                add_vertical_space(1)
                col4, col5, col6 = st.columns([0.3, 0.3, 0.4], gap='medium')

                with col4:
                    user_id = st.text_input(label='User ID ')
                    add_vertical_space(1)
                    add_user = st.form_submit_button(label='Add User')
                    add_vertical_space(1)

                with col5:
                    password = st.text_input(label='Password ', type='password')

                with col6:
                    # Create the target folder if it doesn't exist
                    os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)

                    # Check Subfolders inside the concepts folder or not
                    if len(os.listdir(os.path.join('Result','handwriting','matched','concepts')))==0:
                        option = ['admin', 'teacher', 'student']
                    else:
                        option = ['admin', 'teacher', 'student'] +\
                                 [f'assistant - {i}' for i in os.listdir(os.path.join('Result','handwriting','matched','concepts'))]
                                
                    # Get User Input 
                    role = st.selectbox(label='Role ', options=option)

            if add_user and user_id != '' and password != '':
                add_vertical_space(1)
                sql.add_user_login_credentials_table(user_id, password, role)

        except Exception as e:
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)


    def add_multiple_users():

        add_vertical_space(1)
        try:
            with st.form('Add Multiple Users'):
                add_vertical_space(1)
                # Upload File from User and Submit Button
                login_data_file = st.file_uploader(label='Upload LogIn Data File:', type=['csv', 'xlsx'])
                add_vertical_space(1)
                add_users = st.form_submit_button(label='Add Users')
                add_vertical_space(1)

            if login_data_file is not None and add_users:
                add_vertical_space(1)
                with st.spinner('Processing...'):
                    # Verify the File Type for Reading method
                    if login_data_file.name.endswith('.csv'):
                        df = pd.read_csv(login_data_file)

                    elif login_data_file.name.endswith('.xlsx'):
                        df = pd.read_excel(login_data_file)

                    # Encoded to Password into Hashed Password and Stored in New Column
                    df['password'] = df['password'].apply(lambda x: sql.encode_password(x))

                    # Migrate the Data to SQL table
                    sql.add_multiple_user_login_credentials_table(df)

                # Display the Success Message
                st.markdown(f'<h5 style="text-position:center;color:green;">Users Added Successfully</h5>', unsafe_allow_html=True)
                
                # Trigger a rerun to Refresh the Page
                st.experimental_rerun()
        

        except Exception as e:
            # Display the Error Message
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)
        

    def update_user():

        try:
            add_vertical_space(1)
            with st.form('Update User'):
                add_vertical_space(1)
                col7, col8, col9 = st.columns([0.3, 0.3, 0.4], gap='medium')

                with col7:
                    user_id = st.selectbox(label='User ID  ', options=sql.user_id())
                    add_vertical_space(1)
                    update_user = st.form_submit_button(label='Update User')
                    add_vertical_space(1)

                with col8:
                    password = st.text_input(label='Password ', type='password')

                with col9:
                    # Create the target folder if it doesn't exist
                    os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)

                    # Check Subfolders inside the concepts folder or not
                    if len(os.listdir(os.path.join('Result','handwriting','matched','concepts')))==0:
                        option = ['admin', 'teacher', 'student']
                    else:
                        option = ['admin', 'teacher', 'student'] +\
                                [f'assistant - {i}' for i in os.listdir(os.path.join('Result','handwriting','matched','concepts'))] +\
                                [f'supersub - {i}' for i in os.listdir(os.path.join('Result','handwriting','matched','concepts'))] + ['inactive']

                    # Get User Input 
                    role = st.selectbox(label='Role ', options=option)

            if update_user and password != '':
                add_vertical_space(1)
                sql.update_user_login_credentials_table(user_id, password, role)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)


    def get_role_delete_user(user_id):

        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select role from login_credentials
                           where user_id = '{user_id}' 
                           order by role;''')

        result = cursor.fetchall()

        role_list = [i[0] for i in result]

        return role_list


    def delete_user():

        try:
            add_vertical_space(1)
            col10, col11 = st.columns([0.5, 0.5], gap='medium')

            with col10:
                user_id = st.selectbox(label='User ID   ', options=sql.user_id())
                add_vertical_space(1)
                delete_user = st.button(label='Delete User')
                add_vertical_space(1)

            with col11:
                role = st.selectbox(label='Role   ', options=admin.get_role_delete_user(user_id))

            if delete_user:
                add_vertical_space(1)
                sql.delete_user_login_credentials_table(user_id, role=role)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)


    def main():

        try:
            user_id, login_status = admin.account_login(role='admin')

            if login_status == 'LogIn Successfully':
                add_vertical_space(2)

                col1, col2, col3 = st.columns([0.1, 0.8, 0.1], gap='medium')

                with col2:
                    tab1, tab2, tab3, tab4 = st.tabs(['View User', 'Add User', 'Update User', 'Delete User'])

                    with tab1:
                        add_vertical_space(1)
                        admin.view_user()

                    with tab2:
                        # Add Single User Data in SQL Table
                        add_vertical_space(2)
                        st.markdown(f'<h4 style="color:orange;">Add Single User:</h4>', unsafe_allow_html=True)
                        admin.add_user()

                        # Add Multiple Users Data in SQL Table
                        add_vertical_space(2)
                        st.markdown(f'<h4 style="color:orange;">Add Multiple Users:</h4>', unsafe_allow_html=True)
                        admin.add_multiple_users()

                    with tab3:
                        add_vertical_space(1)
                        admin.update_user()

                    with tab4:
                        add_vertical_space(1)
                        admin.delete_user()

        except TypeError:
            pass



class teacher:

    # Function to load and preprocess images from a folder
    def load_images(folder_path):

        images = []

        for file_name in os.listdir(folder_path):

            image_path = os.path.join(folder_path, file_name)
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            try:
                image = cv2.resize(image, (128, 128))
                images.append(image)
            except:
                pass

        return images


    def model_training():

        with st.spinner('Loading the images and labels'):
            data_path = os.path.join('Dataset','images')

            writers = os.listdir(path=os.path.join('Dataset','images'))
            images = []
            labels = []

            for writer_id, writer in enumerate(writers):
                writer_folder = os.path.join(data_path, writer)

                writer_images = teacher.load_images(writer_folder)

                images.extend(writer_images)
                labels.extend([writer_id] * len(writer_images))

                # Convert images and labels to numpy arrays
        with st.spinner('Converting images and labels to numpy arrays'):
            images = np.array(images) / 255.0  # Normalize pixel values
            labels = np.array(labels)

            # Split dataset into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

        # Define the CNN model architecture
        with st.spinner('Define the CNN model architecture and compiling'):
            model = models.Sequential([
                layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(64, (3, 3), activation='relu'),
                layers.MaxPooling2D((2, 2)),
                layers.Flatten(),
                layers.Dense(64, activation='relu'),
                layers.Dense(len(writers), activation='softmax')
            ])

            # Compile the model
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        with st.spinner('Training the model'):
            model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

        # Evaluate the model
        with st.spinner('Evaluate the model'):
            loss, accuracy = model.evaluate(X_test, y_test)

            # Create the target folder if it doesn't exist
            os.makedirs(r'Model', exist_ok=True)

            # Save the trained model
            model.save(os.path.join('Model','trained_model.h5'))


    def model():
        try:
            add_vertical_space(2)
            col1, col2 = st.columns([0.5, 0.5])

            with col1:
                option = st.text_input(label='Please Enter the Student ID:')
                add_vertical_space(1)
                submit = st.button(label='Submit ')

            if submit and option != '':

                if option in os.listdir(os.path.join('Dataset','images')):
                    add_vertical_space(2)
                    teacher.model_training()
                    st.markdown(f'<h5 style="color: green;">Model Trained Successfully</h5>', unsafe_allow_html=True)

                else:
                    add_vertical_space(2)
                    st.markdown(f'<h5 style="color: orange;">{option} Handwriting Samples are not available</h5>',
                                unsafe_allow_html=True)

        except ValueError:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color: orange;">Handwriting Sample Images are required for Model Training</h5>',
                        unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color: orange;">{e}</h5>', unsafe_allow_html=True)


    def predict_writer(input_image):
        try:
            os.makedirs(r'Model', exist_ok=True)  # Create the target folder if it doesn't exist

            model = load_model(os.path.join('Model','trained_model.h5'))  # Load the trained model

            image = Image.open(input_image)  # Convert PIL image to BytesIO object

            image_np = np.array(image.convert('L'))  # Convert to grayscale

            resized_image = cv2.resize(image_np, (128, 128))  # Resize image to match model input shape

            preprocessed_image = resized_image / 255.0  # Normalize pixel values

            input_data = np.expand_dims(preprocessed_image, axis=0)  # Add batch dimension

            predictions = model.predict(input_data)

            writer_id = np.argmax(predictions)

            return writer_id

        except OSError:
            st.markdown(f'<h5 style="color:orange;">Trained Model is Required for Handwriting Verification</h5>',
                        unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<h5 style="color:orange;">{e}</h5>', unsafe_allow_html=True)


    def handwriting_verification():

        add_vertical_space(2)
        with st.form('Handwriting Verification'):

            add_vertical_space(1)
            # teacher upload the Student Answer Sheet images for Handwriting verification
            answer_sheet_images = st.file_uploader(label='Upload Answer Sheets:', type=['jpg', 'jpeg', 'png'],
                                                   accept_multiple_files=True)

            add_vertical_space(1)
            submit = st.form_submit_button(label='Submit')
            add_vertical_space(1)

        if submit and answer_sheet_images != []:

            add_vertical_space(1)
            with st.spinner('Verifying Handwriting...'):

                for i, answer_sheet_image in enumerate(answer_sheet_images):

                    answer_sheet_name = answer_sheet_image.name  # Ex: ST01_machine learning_Q101.jpeg

                    # Get Student ID from Answer Sheet Name ---------------> [Ex: ST01, machine learning, Q101.jpeg] --> ST01
                    student_id = answer_sheet_name.split('_')[0]
                    concept = answer_sheet_name.split('_')[1]

                    # Predict the writer from the input image
                    predicted_writer_id = teacher.predict_writer(answer_sheet_image)

                    # List of writer names corresponding to their IDs
                    writer_names = os.listdir(os.path.join('Dataset','images'))

                    # Get the predicted writer's name
                    predicted_writer_name = writer_names[predicted_writer_id]

                    # Compare the predicted writer with the actual writer
                    if student_id == predicted_writer_name:
                        img = Image.open(answer_sheet_image)

                        # Create the target folder if it doesn't exist
                        os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)
                        img.save(os.path.join('Result','handwriting','matched','concepts',concept,answer_sheet_name))

                        # Create the student_id folder if it doesn't exist
                        os.makedirs(os.path.join('Result','handwriting','matched','students',student_id), exist_ok=True)
                        img.save(os.path.join('Result','handwriting','matched','students',student_id,answer_sheet_name))

                    else:
                        img = Image.open(answer_sheet_image)

                        # Create the target folder if it doesn't exist
                        os.makedirs(os.path.join('Result','handwriting','mismatched'), exist_ok=True)   # os.path.join('Result','handwriting','mismatched')
                        img.save(os.path.join('Result','handwriting','mismatched', answer_sheet_name))

                # Create the target folder if it doesn't exist
                os.makedirs(os.path.join('Result','handwriting','mismatched'), exist_ok=True)

                # Make List for Mismatched Handwriting Images
                mismatch_image_list = os.listdir(os.path.join('Result','handwriting','mismatched'))

                # If All Images are Matched
                if len(mismatch_image_list) == 0:
                    st.markdown(
                        f'<h5 style="text-align: center;color: green;">All Answer Sheets are Handwriting Matched</h5>',
                        unsafe_allow_html=True)

                else:
                    mismatch_image_dict = {'user_id': [], 'concept': [], 'question_number': []}

                    for i in mismatch_image_list:
                        mismatched_user_id = i.split('_')[0]
                        mismatched_concept = i.split('_')[1]
                        mismatched_question_number = i.split('_')[2].split('.')[0]
                        mismatch_image_dict['user_id'].append(mismatched_user_id)
                        mismatch_image_dict['concept'].append(mismatched_concept)
                        mismatch_image_dict['question_number'].append(mismatched_question_number)

                    mismatch_image_df = pd.DataFrame(mismatch_image_dict)
                    add_vertical_space(1)
                    st.markdown(f'<h5 style="color: orange;">Mismatched Handwriting Details:</h5>',
                                unsafe_allow_html=True)
                    add_vertical_space(1)
                    st.dataframe(mismatch_image_df)


    def delete_data_test_qa_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''delete from test_qa;''')
            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def test_qa_upload():

        add_vertical_space(1)
        test_qa = st.file_uploader(label='', type=['csv', 'xlsx'])
        
        if test_qa is not None:

            with st.spinner('Uploading the Test QA...'):

                # Verify the File Type for Reading method
                if test_qa.name.endswith('.csv'):
                    df = pd.read_csv(test_qa)

                elif test_qa.name.endswith('.xlsx'):
                    df = pd.read_excel(test_qa)

                # Deleting the Previous QA Data from test_qa table
                teacher.delete_data_test_qa_table()

                # Uploading the New QA Data to test_qa table
                sql.migrate_test_qa_table(df)


    def user_id():

        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select distinct user_id from login_credentials
                           where role not in ('admin', 'teacher')
                           order by user_id;''')

        result = cursor.fetchall()

        user_id = [i[0] for i in result]

        return user_id


    def view_user():
        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select user_id, role from login_credentials
                           where role not in ('admin','teacher')
                           order by user_id;''')
        result = cursor.fetchall()

        index = [i for i in range(1, len(result) + 1)]
        columns = [i[0] for i in cursor.description]

        df = pd.DataFrame(result, columns=columns, index=index)
        df = df.rename_axis('s.no')
        df = pd.DataFrame(df)
        st.dataframe(df)


    def update_user_role(user_id, role):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''update login_credentials
                               set role='{role}'
                               where user_id='{user_id}';''')
            connection.commit()

            st.markdown(f'<h5 style="color: green;">User Role Updated Successfully</h5>', unsafe_allow_html=True)
            # Trigger a rerun to Refresh the Page
            st.experimental_rerun()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def update_user():

        try:
            add_vertical_space(1)
            with st.form('Update User'):
                add_vertical_space(1)
                col1, col2 = st.columns([0.5, 0.5], gap='medium')

                with col1:
                    user_id = st.selectbox(label='User ID  ', options=teacher.user_id())

                with col2:
                    # Create the target folder if it doesn't exist
                    os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)

                    # Check Subfolders inside the concepts folder or not
                    if len(os.listdir(os.path.join('Result','handwriting','matched','concepts')))==0:
                        option = ['admin', 'teacher', 'student']
                    else:
                        option = ['student'] + [f'assistant - {i}' for i in os.listdir(os.path.join('Result','handwriting','matched','concepts'))] +\
                                [f'supersub - {i}' for i in os.listdir(os.path.join('Result','handwriting','matched','concepts'))] + ['inactive']

                    # Get User Input 
                    role = st.selectbox(label='Role  ', options=option)

                add_vertical_space(1)
                update_user = st.form_submit_button(label='Update User')
                add_vertical_space(1)

            if update_user:
                add_vertical_space(1)
                teacher.update_user_role(user_id, role)

        except Exception as e:
            add_vertical_space(1)
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)


    def get_test_id_list():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select distinct test_id from student_test;''')
            connection.commit()

            result = cursor.fetchall()

            if len(result) > 0:
                df = pd.DataFrame(result)
                df = df[0].to_list()
                df.sort(reverse=False)
                return df

            else:
                return []

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def get_student_id_list_test():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select distinct student_id from student_test;''')
            connection.commit()

            result = cursor.fetchall()

            if len(result) > 0:
                df = pd.DataFrame(result)
                df = df[0].to_list()
                df.sort(reverse=False)
                return df

            else:
                return []

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_test_status():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, test_id, concept, sum(mark) as mark
                            from student_test 
                            group by student_id, test_id, concept
                            order by test_id, concept asc, mark desc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def filter_student_test_status(condition):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, test_id, concept, sum(mark) as mark
                               from student_test 
                               where {condition} 
                               group by student_id, test_id, concept
                               order by test_id, concept asc, mark desc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def get_exam_id_list():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select distinct exam_id from student_exam;''')
            connection.commit()

            result = cursor.fetchall()

            if len(result) > 0:
                df = pd.DataFrame(result)
                exam_id_list = df[0].to_list()
                exam_id_list.sort(reverse=False)
                return exam_id_list

            else:
                return []

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def get_student_id_list_exam():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select distinct student_id from student_exam;''')
            connection.commit()

            result = cursor.fetchall()

            if len(result) > 0:
                df = pd.DataFrame(result)
                df = df[0].to_list()
                df.sort(reverse=False)
                return df

            else:
                return []

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_exam_status():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, mark, evaluator_id
                               from student_exam 
                               group by student_id, exam_id, concept, question_no, mark, evaluator_id
                               order by question_no, concept, exam_id asc, mark desc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def filter_student_exam_status(condition):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, mark, evaluator_id
                            from student_exam 
                            where {condition}
                            group by student_id, exam_id, concept, question_no, mark, evaluator_id
                            order by question_no, concept, exam_id asc, mark desc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_exam_status_average():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, avg(mark) as mark
                               from student_exam 
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_exam_status_maximum():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, max(mark) as mark
                               from student_exam  
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def filter_student_exam_status_average(condition):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, avg(mark) as mark
                               from student_exam 
                               where {condition}
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def filter_student_exam_status_maximum(condition):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, max(mark) as mark
                               from student_exam  
                               where {condition}
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_student_exam_status_average(exam_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, avg(mark) as mark
                               from student_exam 
                               where exam_id='{exam_id}' 
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_student_exam_status_maximum(exam_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select student_id, exam_id, concept, question_no, max(mark) as mark
                               from student_exam 
                               where exam_id='{exam_id}'  
                               group by student_id, exam_id, concept, question_no
                               order by exam_id, student_id, question_no asc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def update_answer_sheet_upload_portal(status):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''update status
                               set status='{status}'
                               where identifier='upload_portal';''')
            connection.commit()

            if status == 'open':
                st.markdown(f'<h5 style="color: green;">Answer Sheet Upload Portal Opened Successfully</h5>',
                            unsafe_allow_html=True)
            elif status == 'close':
                st.markdown(f'<h5 style="color: green;">Answer Sheet Upload Portal Closed Successfully</h5>',
                            unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def mark_delete_student_marks_table(exam_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''delete from student_marks
                               where exam_id='{exam_id}';''')
            connection.commit()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def migrate_student_marks_table(df, identifier, status):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.executemany(f'''insert into student_marks(student_id, exam_id, concept, question_no, mark) 
                                   values(%s,%s,%s,%s,%s);''', df.values.tolist())
            connection.commit()

            # Update Status table
            sql.migrate_status_table(identifier, status)

            st.markdown(f'<h5 style="color: green;">Marks Updated Successfully</h5>', unsafe_allow_html=True)
            # Trigger a rerun to Refresh the Page
            st.experimental_rerun()

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def view_status_table():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select * from status;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            st.dataframe(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def marks_approval_status_update():

        col1, col2, col3 = st.columns([0.4, 0.4, 0.2], gap='medium')
        with col1:
            identifier = st.selectbox(label='identifier', options=['upload_portal'] + teacher.get_exam_id_list())
        with col2:
            if identifier == 'upload_portal':
                status = st.selectbox(label='status', options=['close', 'open'])
            else:
                status = st.selectbox(label='status ', options=['remove', 'average marks', 'maximum marks'])

        add_vertical_space(1)
        update = st.button('Update')
        add_vertical_space(1)

        if update and identifier == 'upload_portal' and status == 'open':
            teacher.update_answer_sheet_upload_portal(status='open')

        elif update and identifier == 'upload_portal' and status == 'close':
            teacher.update_answer_sheet_upload_portal(status='close')

        elif update and identifier != 'upload_portal' and status == 'remove':
            teacher.mark_delete_student_marks_table(exam_id=identifier)
            sql.delete_exam_marks_status_table(identifier, status)
            add_vertical_space(2)
            st.markdown(f'<h5 style="color: green;">Marks Removed Successfully</h5>', unsafe_allow_html=True)

        elif update and identifier != 'upload_portal' and status == 'average marks':
            # Remove Existing Old Marks from table
            teacher.mark_delete_student_marks_table(exam_id=identifier)
            sql.delete_exam_marks_status_table(identifier, status)
            # Add Average Marks in the table
            df = teacher.migrate_student_exam_status_average(exam_id=identifier)
            teacher.migrate_student_marks_table(df, identifier, status)

        elif update and identifier != 'upload_portal' and status == 'maximum marks':
            # Remove Existing Old Marks from table
            teacher.mark_delete_student_marks_table(exam_id=identifier)
            sql.delete_exam_marks_status_table(identifier, status)
            # Add Maximum Marks in the table
            df = teacher.migrate_student_exam_status_maximum(exam_id=identifier)
            teacher.migrate_student_marks_table(df, identifier, status)


    def student_status():

        # Student Test Status
        add_vertical_space(2)
        st.markdown(f'<h4 style="color:green;">Student Test Status</h4>', unsafe_allow_html=True)

        if len(teacher.get_test_id_list()) > 0:
            col1, col2 = st.columns([0.5, 0.5], gap='medium')
            with col1:
                test_options = ['Over All'] + teacher.get_test_id_list()
                test_id = st.selectbox(label='Select Test ID', options=test_options)
            with col2:
                student_id_options = ['Over All'] + teacher.get_student_id_list_test()
                student_id = st.selectbox(label='Select Student ID', options=student_id_options)

            add_vertical_space(2)
            if test_id == 'Over All' and student_id == 'Over All':
                teacher.student_test_status()
            elif test_id == 'Over All' and student_id != 'Over All':
                teacher.filter_student_test_status(f"student_id='{student_id}'")
            elif test_id != 'Over All' and student_id == 'Over All':
                teacher.filter_student_test_status(f"test_id='{test_id}'")
            elif test_id != 'Over All' and student_id != 'Over All':
                teacher.filter_student_test_status(f"test_id='{test_id}' and student_id='{student_id}'")

        else:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color:orange;">No Records Found</h5>', unsafe_allow_html=True)

        # Student Exam Status
        add_vertical_space(2)
        st.markdown(f'<h4 style="color:green;">Student Exam Status</h4>', unsafe_allow_html=True)

        if len(teacher.get_exam_id_list()) > 0:
            col3, col4 = st.columns([0.5, 0.5], gap='medium')
            with col3:
                exam_options = ['Over All'] + teacher.get_exam_id_list()
                exam_id = st.selectbox(label='Select Exam ID', options=exam_options)
            with col4:
                student_id_options = ['Over All'] + teacher.get_student_id_list_exam()
                student_id = st.selectbox(label='Select Student ID ', options=student_id_options)

            add_vertical_space(2)
            if exam_id == 'Over All' and student_id == 'Over All':
                teacher.student_exam_status()

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Average Marks:</h5>', unsafe_allow_html=True)
                teacher.student_exam_status_average()

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Maximum Marks:</h5>', unsafe_allow_html=True)
                teacher.student_exam_status_maximum()


            elif exam_id == 'Over All' and student_id != 'Over All':
                teacher.filter_student_exam_status(f"student_id='{student_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Average Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_average(f"student_id='{student_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Maximum Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_maximum(f"student_id='{student_id}'")


            elif exam_id != 'Over All' and student_id == 'Over All':
                teacher.filter_student_exam_status(f"exam_id='{exam_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Average Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_average(f"exam_id='{exam_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Maximum Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_maximum(f"exam_id='{exam_id}'")


            elif exam_id != 'Over All' and student_id != 'Over All':
                teacher.filter_student_exam_status(f"exam_id='{exam_id}' and student_id='{student_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Average Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_average(f"exam_id='{exam_id}' and student_id='{student_id}'")

                add_vertical_space(2)
                st.markdown(f'<h5 style="color:orange;">Maximum Marks:</h5>', unsafe_allow_html=True)
                teacher.filter_student_exam_status_maximum(f"exam_id='{exam_id}' and student_id='{student_id}'")

        else:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color:orange;">No Records Found</h5>', unsafe_allow_html=True)

        add_vertical_space(3)
        st.markdown(f'<h5 style="color:green;">Status:</h5>', unsafe_allow_html=True)
        teacher.marks_approval_status_update()

        # Viwe Status Table
        add_vertical_space(1)
        with st.expander(label='Status:'):
            teacher.view_status_table()


    def main():

        try:
            user_id, login_status = admin.account_login(role='teacher')

            if login_status == 'LogIn Successfully':
                add_vertical_space(2)
                col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                with col2:
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(
                        ['Model Training', 'Handwriring Verification', 'Test QA Upload',
                         'Update Role', 'Student Status'])
                    with tab1:
                        teacher.model()

                    with tab2:
                        teacher.handwriting_verification()

                    with tab3:
                        teacher.test_qa_upload()

                    with tab4:
                        add_vertical_space(2)
                        teacher.update_user()
                        add_vertical_space(2)
                        with st.expander('View User'):
                            teacher.view_user()

                    with tab5:
                        teacher.student_status()


        except TypeError:
            pass



class student:

    def retrive_qa():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select * from test_qa;''')

            s = cursor.fetchall()

            index = [i for i in range(1, len(s) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(s, columns=columns, index=index)
            df = df.rename_axis('s.no')
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_test_status_verification(student_id, test_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select * from student_test
                            where student_id='{student_id}' and test_id='{test_id}';''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            return df

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def test_id_and_question_selection(df):

        # Display Test ID and Student can select the Question Number
        col1, col3 = st.columns([0.8, 0.2])

        with col1:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align: center; color: orange;">Test ID: {df.iloc[0, 0]}</h5>',
                        unsafe_allow_html=True)

        with col3:
            question_number = st.number_input(label='', min_value=1, max_value=len(df), value=1, step=1)

        return question_number


    def test_qa_form(question_number, df):

        # Display the Questions with Options in Test Tab
        with st.form('student_test'):
            # question number match to index number to retrieve QA from dataframe
            i = question_number - 1

            question_no = df.iloc[i, 2]
            question_text = df.iloc[i, 3]
            option_a = df.iloc[i, 4]
            option_b = df.iloc[i, 5]
            option_c = df.iloc[i, 6]
            option_d = df.iloc[i, 7]

            question = f'Q{question_no}. {question_text}'
            options = [option_a, option_b, option_c, option_d]

            # Display the Question and Options
            student_option = st.radio(label=question, options=options, index=None)

            submit = st.form_submit_button(label='Submit')

            return student_option, submit


    def write_test(user_id, df, test_status_df):

        # data stored in session state ---> because page automatically refreshed when select the next question, so saved data Erased automatically.
        if 'test_data' not in st.session_state:
            st.session_state.test_data = {'student_id': [], 'test_id': [], 'concept': [],
                                          'question_no': [], 'question': [], 'answer': [], 'mark': []}

        if len(test_status_df) == 0:

            # Display the test_id and student select question number
            question_number = student.test_id_and_question_selection(df)
            i = question_number - 1

            # Display the Questions with Options in Test Tab
            student_option, submit = student.test_qa_form(question_number, df)

            # Store the data in session state
            if submit and student_option is not None:

                if question_number not in st.session_state.test_data['question_no']:
                    st.session_state.test_data['student_id'].append(user_id)
                    st.session_state.test_data['test_id'].append(df.iloc[0, 0])
                    st.session_state.test_data['question_no'].append(question_number)
                    st.session_state.test_data['concept'].append(df.iloc[i, 1])
                    st.session_state.test_data['question'].append(df.iloc[i, 3])
                    st.session_state.test_data['answer'].append(student_option)
                    st.session_state.test_data['mark'].append(1 if student_option == df.iloc[i, 8] else 0)

                # Update the Answer and Mark in session state
                else:
                    st.session_state.test_data['answer'][i] = student_option
                    st.session_state.test_data['mark'][i] = 1 if student_option == df.iloc[i, 8] else 0


            elif submit:
                st.markdown(f'<h5 style="color:orange;">Please Select an option</h5>', unsafe_allow_html=True)

            # Display the Test Status
            with st.expander(label='View Test Status'):
                expander_df = pd.DataFrame(st.session_state.test_data, 
                                              columns=['student_id', 'test_id', 'concept', 'question_no', 
                                                       'question', 'answer', 'mark'])
                expander_df.drop(columns=['student_id', 'test_id', 'mark'], inplace=True)
                expander_df = expander_df.sort_values(by='question_no', ascending=True)
                expander_df = expander_df.reset_index(drop=True)
                st.dataframe(expander_df)

            # Finish test
            add_vertical_space(1)
            finish = st.button(label='Finish')

            # make a dataframe & Sort by question_no and Reset index
            test_df = pd.DataFrame(st.session_state.test_data, 
                                       columns=['student_id', 'test_id', 'concept', 'question_no', 
                                                'question', 'answer', 'mark'])
            test_df = test_df.sort_values(by='question_no', ascending=True)
            test_df = test_df.reset_index(drop=True)

            # migrate the data into student_test table in SQL
            if finish and len(df) == len(test_df):
                sql.migrate_student_test_table(test_df)

            elif finish:
                st.markdown(f'<h5 style="color: orange;">Test Incomplete! Answer all questions before submitting</h5>',
                            unsafe_allow_html=True)

        else:
            add_vertical_space(2)
            st.markdown(f'<h3 style="text-align:center; color:orange;">No Pending Tests</h3>', unsafe_allow_html=True)


    def student_test_status(student_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select test_id, concept, sum(mark) as mark
                               from student_test
                               where student_id='{student_id}'
                               group by test_id, concept
                               order by test_id asc, mark desc;''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            if len(df) > 0:
                st.dataframe(df)
                return df
            else:
                st.markdown(f'<h5 style="color:orange;">No Records Found</h5>', unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def student_exam_status(student_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select * from student_marks
                               where student_id = '{student_id}';''')
            result = cursor.fetchall()

            index = [i for i in range(1, len(result) + 1)]
            columns = [i[0] for i in cursor.description]

            df = pd.DataFrame(result, columns=columns, index=index)
            df = df.rename_axis('s.no')
            df = pd.DataFrame(df)
            if len(df) > 0:
                st.dataframe(df)
                return df
            else:
                st.markdown(f'<h5 style="color:orange;">No Records Found</h5>', unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def main():

        try:
            user_id, login_status = admin.account_login(role='student')

            if login_status == 'LogIn Successfully':

                add_vertical_space(2)

                tab1, tab2,= st.tabs(['Test', 'Status'])

                with tab1:
                    add_vertical_space(1)

                    # Retrieve Test QA from test_qa SQL table
                    df = student.retrive_qa()

                    # Verify Test QA was uploaded from teacher or not
                    if len(df) > 0:
                        # Verify if the student has taken the test or not
                        test_status_df = student.student_test_status_verification(user_id, df.iloc[0, 0])

                        student.write_test(user_id, df, test_status_df)

                    else:
                        add_vertical_space(2)
                        st.markdown(f'<h3 style="text-align:center; color:orange;">No Pending Tests</h3>',
                                    unsafe_allow_html=True)



                with tab2:
                    add_vertical_space(2)
                    col1, col2 = st.columns([0.5, 0.5])
                    with col1:
                        st.markdown(f'<h4 style="color:green;">Test Status</h4>', unsafe_allow_html=True)
                        add_vertical_space(1)
                        student.student_test_status(student_id=user_id)

                    with col2:
                        st.markdown(f'<h4 style="color:green;">Exam Status</h4>', unsafe_allow_html=True)
                        add_vertical_space(1)
                        student.student_exam_status(student_id=user_id)


        except TypeError:
            pass

        except Exception as e:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color:orange;">{e}</h5>', unsafe_allow_html=True)



class supersub:

    def user_role_identification(user_id):

        connection = psycopg2.connect(host=os.getenv('HOST'),
                                      user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        cursor.execute(f'''select role from login_credentials
                           where user_id='{user_id}';''')
        result = cursor.fetchall()

        return result[0][0]


    def update_student_exam_table(student_id, exam_id, question_no, concept, mark, evaluator_id):

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''insert into student_exam(student_id, exam_id, concept, question_no, mark, evaluator_id) 
                               values('{student_id}','{exam_id}','{concept}',{question_no},{mark},'{evaluator_id}');''')
            connection.commit()

            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align:center; color:green;">Mark Updated Successfully</h5>',
                        unsafe_allow_html=True)

        # unique violation
        except psycopg2.errors.UniqueViolation:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align:center; color:orange;">Mark Already Updated</h5>',
                        unsafe_allow_html=True)

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align:center; color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def display_answer_sheet(pending_evaluation_list, user_id, concept, evaluation_path):

        # Get Question Number from Answer Sheet Name ( ["ST01_sql_Q9.jpeg"] ------> 'Q9' )

        question_number = pending_evaluation_list[0].split('.')[0].split('_')[2]

        title_format = f"Answer Sheet: {concept} - {question_number}"

        # Display Title
        add_vertical_space(1)
        col1, col2 = st.columns([0.7, 0.3], gap='medium')
        with col1:
            answer_sheet = os.path.join(evaluation_path, pending_evaluation_list[0])
            st.markdown(f'<h5 style="color:orange;text-align:center">{title_format}</h5>', unsafe_allow_html=True)
        with col2:
            st.markdown(
                f'<h5 style="color:orange;text-align:center">Pending Evaluation: {len(pending_evaluation_list)}</h5>',
                unsafe_allow_html=True)

        # Display the Resized Answer Sheet Images
        add_vertical_space(1)
        img = Image.open(answer_sheet)
        img_1 = img.resize((900, 900))
        st.image(img_1, use_column_width=True)

        # Save the Original Size Answer Sheet into Evaluation Folder
        add_vertical_space(1)
        next_button = st.button(label='Next')

        if next_button:
            evaluation_image_path = os.path.join('Result','evaluation',user_id,concept,pending_evaluation_list[0])
            img.save(evaluation_image_path)

            # Trigger a rerun to Refresh the Page and Display the Next Answer Sheet
            st.experimental_rerun()


    def mark_update_student_exam_table(student_id, concept, user_id):

        # Update the Mark in Student Exam Table
        add_vertical_space(2)
        with st.form('Answer Sheet'):
            add_vertical_space(1)
            col1, col2, col3 = st.columns([0.3, 0.3, 0.3], gap='medium')

            with col1:
                exam_id = st.text_input(label='Enter Exam ID')
            with col2:
                question_no = st.number_input(label="Select Question Number", value=1, step=1)
            with col3:
                mark = st.text_input(label="Enter Mark")

            add_vertical_space(1)
            update = st.form_submit_button(label='Update')
            add_vertical_space(1)

        add_vertical_space(2)
        if update and exam_id != '' and mark != '':
            supersub.update_student_exam_table(student_id, exam_id, question_no, concept, int(mark),
                                               evaluator_id=user_id)

        elif update:
            if exam_id == '':
                st.markdown(f'<h5 style="text-align:center; color:orange;">Exam ID is Empty</h5>', unsafe_allow_html=True)
            elif  exam_id != '' and mark == '':
                st.markdown(f'<h5 style="text-align:center; color:orange;">Mark is Empty</h5>', unsafe_allow_html=True)
        

    def evaluation(user_id):

        # Find out the User Role based on User ID
        user_role = supersub.user_role_identification(user_id)

        # Find out the Concept of Supersub
        concept = user_role.split('-')[-1].strip()

        # Create the target folder if it doesn't exist
        os.makedirs(os.path.join('Result','evaluation',user_id,concept), exist_ok=True)
        os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)

        # Evaluted Answer Sheet List
        evauated_answer_sheet_list = os.listdir(os.path.join('Result','evaluation',user_id,concept))

        # Make Path to Access Answer Sheets
        evaluation_path = os.path.join('Result','handwriting','matched','concepts',concept)

        # Get a List of all Answer Sheet names and Sort by Question Number Ascending
        answer_sheet_list = os.listdir(evaluation_path)
        answer_sheet_list = sorted(answer_sheet_list,
                                   key=lambda x: int(x.split('_')[-1].split('.')[0].replace('Q', '')))

        # Compare Answer Sheet List with Evaluated Answer Sheet List
        pending_evaluation_list = [i for i in answer_sheet_list if i not in evauated_answer_sheet_list]

        if len(pending_evaluation_list) > 0:

            # Get Student ID from Answer Sheet Name ( ["ST01_sql_Q9.jpeg"] ------> 'ST01' )
            student_id = pending_evaluation_list[0].split('.')[0].split('_')[0]

            supersub.display_answer_sheet(pending_evaluation_list, user_id, concept, evaluation_path)

            supersub.mark_update_student_exam_table(student_id, concept, user_id)

        else:
            st.markdown(f'<h3 style="color:orange;text-align:center">No Pending Evaluation</h3>',
                        unsafe_allow_html=True)


    def check_upload_portal_status():

        try:
            connection = psycopg2.connect(host=os.getenv('HOST'),
                                          user=os.getenv('USER'),
                                          password=os.getenv('PASSWORD'),
                                          database=os.getenv('DATABASE'))
            cursor = connection.cursor()

            cursor.execute(f'''select status from status
                               where identifier='upload_portal';''')

            portal_status = cursor.fetchall()

            return portal_status[0][0]

        except Exception as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

        finally:
            # close the connection
            if connection:
                cursor.close()
                connection.close()


    def upload_answer_sheet():

        add_vertical_space(1)
        try:
            with st.form('Upload Answer Sheet'):

                add_vertical_space(1)
                answer_sheet = st.file_uploader("Upload Answer Sheet", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

                add_vertical_space(1)
                col1, col2, col3, col4,col5 = st.columns([0.2, 0.27, 0.2, 0.2,0.35])
                with col1:
                    student_id=st.text_input(label='Student ID')
                with col2:
                    # Create the target folder if it doesn't exist
                    os.makedirs(os.path.join('Result','handwriting','matched','concepts'), exist_ok=True)
                    os.makedirs(os.path.join('Result','handwriting','mismatched'), exist_ok=True)
                    # User Select the Concept
                    concept = st.selectbox(label="Select Concept", options=os.listdir(os.path.join('Result','handwriting','matched','concepts')))
                with col3:
                    question_start = st.text_input(label="Question Start (Ex: 1)")
                with col4:
                    question_end = st.text_input(label="Question End (Ex: 4)")
                with col5:
                    skipped_questions = st.text_input(label="Skipped Question (Ex: 2, 3) Optional").split(',')
                    skipped_questions = [int(i) for i in skipped_questions if i != '']
                

                add_vertical_space(2)
                upload = st.form_submit_button(label='Upload')
                add_vertical_space(1)

            # User Uploaded the Answer Sheets
            if upload and answer_sheet != []:

                # User Enter the Start and End Question Numbers
                if question_start != '':
                    if question_end != '':
                        question_numbers = [i for i in range(int(question_start), int(question_end) + 1) if
                                            i not in skipped_questions]
                    elif question_end == '' and len(answer_sheet) == 1:
                        question_numbers = [question_start]
                    elif question_end == '' and len(answer_sheet) > 1:
                        add_vertical_space(2)
                        st.markdown(f'<h5 style="text-align:center; color:orange;">End Question Number is Empty</h5>',
                                    unsafe_allow_html=True)

                    # Answer Sheet and Question Numbers are Matched
                    if len(answer_sheet) == len(question_numbers):

                        for i, uploaded_file in enumerate(answer_sheet):
                            question_number = question_numbers[i]

                            file_name = f"{student_id}_{concept}_Q{question_number}.{uploaded_file.type.split('/')[-1]}"

                            # Create the target folder if it doesn't exist
                            os.makedirs(os.path.join('Result','teacher'), exist_ok=True)

                            # save the answer sheet in file path
                            img = Image.open(uploaded_file)
                            img.save(os.path.join('Result','teacher',file_name))

                        add_vertical_space(2)
                        st.markdown(f'<h5 style="text-align:center; color:green;">Answer Sheet Uploaded Successfully</h5>', unsafe_allow_html=True)

                    # Answer Sheets and Question Numbers Mismatched
                    elif len(answer_sheet) != len(question_numbers):
                        add_vertical_space(2)
                        st.markdown(f'<h5 style="text-align:center; color:orange;">Answer Sheets and Question Numbers are Mismatched</h5>', unsafe_allow_html=True)

                # User Forgot to Enter the Start and End Question Numbers
                elif question_start == '' or question_end == '':
                    add_vertical_space(2)
                    st.markdown(f'<h5 style="text-align:center; color:orange;">Start/End Question Number Empty</h5>',
                                unsafe_allow_html=True)

            # User not Uploaded the Answer Sheets
            elif upload and answer_sheet == []:
                add_vertical_space(2)
                st.markdown(f'<h5 style="text-align:center; color:orange;">Please Upload the Answer Sheets</h5>',
                            unsafe_allow_html=True)

        except TypeError as e:
            add_vertical_space(2)
            st.markdown(f'<h5 style="text-align:center; color:orange;">Upload Error: Please Contact teacher</h5>',
                        unsafe_allow_html=True)


    def main():

        try:
            user_id, login_status = admin.account_login(role='supersub')

            if login_status == 'LogIn Successfully':

                add_vertical_space(2)

                tab1, tab2, = st.tabs(['Evaluation', 'Upload Portal'])

                with tab1:
                    add_vertical_space(1)
                    supersub.evaluation(user_id)

                with tab2:
                    add_vertical_space(1)
                    upload_portal_status = supersub.check_upload_portal_status()

                    if upload_portal_status == 'open':
                        supersub.upload_answer_sheet()

                    elif upload_portal_status == 'close':
                        add_vertical_space(2)
                        st.markdown(
                            f'<h3 style="text-align:center; color:orange;">Answer Sheet Upload Portal Closed</h3>',
                            unsafe_allow_html=True)

        except TypeError:
            pass

        except Exception as e:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color:orange;">{e}</h5>', unsafe_allow_html=True)



class assistant(supersub):

    def main():

        try:
            user_id, login_status = admin.account_login(role='assistant')

            if login_status == 'LogIn Successfully':
                
                add_vertical_space(2)
                tab1, tab2, = st.tabs(['Evaluation', 'Upload Portal'])

                with tab1:
                    add_vertical_space(1)
                    assistant.evaluation(user_id)

                with tab2:
                    add_vertical_space(1)
                    upload_portal_status = assistant.check_upload_portal_status()

                    if upload_portal_status == 'open':
                        assistant.upload_answer_sheet()

                    elif upload_portal_status == 'close':
                        add_vertical_space(2)
                        st.markdown(f'<h3 style="text-align:center; color:orange;">Answer Sheet Upload Portal Closed</h3>', unsafe_allow_html=True)


        except TypeError:
            pass

        except Exception as e:
            add_vertical_space(1)
            st.markdown(f'<h5 style="color:orange;">{e}</h5>', unsafe_allow_html=True)




streamlit_config()

with st.sidebar:
    add_vertical_space(4)
    option = option_menu(menu_title='',
                         options=['Admin LogIn', 'Teacher LogIn', 'Assistant LogIn', 'Supersub LogIn', 'Student LogIn', 'Exit'],
                         icons=['database-fill', 'globe', 'bar-chart-line', 'list-task', 'slash-square', 'sign-turn-right-fill'])


if option == 'Admin LogIn':

    # SQL database & table initialization setup
    sql.main()

    admin.main()


elif option == 'Teacher LogIn':

    teacher.main()


elif option == 'Student LogIn':

    student.main()


elif option == 'Supersub LogIn':

    supersub.main()


elif option == 'Assistant LogIn':

    assistant.main()


elif option == 'Exit':

    add_vertical_space(1)
    st.markdown(f'<h3 style="color:orange;text-align:center">Thank you for your time. Exiting the application</h3>',
                unsafe_allow_html=True)
    st.balloons()

