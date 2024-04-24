import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import base64
import io
import mysql.connector

def image_to_text(path):

  input_image = Image.open(path)

  #convering image to array format

  image_array = np.array(input_image)

  reader = easyocr.Reader(['en'])
  text = reader.readtext(image_array, detail = 0)

  return text, input_image

def extracted_text(text):

  ext_dic = {"Name":[], "Designation":[], "Contacts":[], "Email":[], "Company_Name":[], "Website":[], "Address":[], "Pincode":[]}

  ext_dic["Name"].append(text[0])
  ext_dic["Designation"].append(text[1])

  for i in range(2,len(text)):

    if text[i].startswith("+") or (text[i].replace("-","").isdigit() and '-' in text[i]):

      ext_dic["Contacts"].append(text[i])

    elif "@" in text[i] and ".com" in text[i]:

      ext_dic["Email"].append(text[i])

    elif "www" in text[i] or "wwW" in text[i] or "wWw" in text[i] or "Www" in text[i] or "wWW" in text[i] or "WWw" in text[i] or "WwW" in text[i] or "WWW" in text[i] and ".com" in text[i]:

      small = text[i].lower()
      ext_dic["Website"].append(small)

    elif "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or text[i].isdigit():

      ext_dic["Pincode"].append(text[i])

    elif re.match(r'^[A-Za-z]', text[i]):

      ext_dic["Company_Name"].append(text[i])

    else:

      remove_coln = re.sub(r'[,;]','',text[i])
      ext_dic["Address"].append(remove_coln)

  for key, value in ext_dic.items():

    if len(value)>0:
      concadenate = " ".join(value)
      ext_dic[key] = [concadenate]

    else:
      value = "NA"
      ext_dic[key] = [value]

  return ext_dic

#Streamlit UI

st.set_page_config(layout="wide")

st.header("BizCard - Extracting Business Card Data with OCR")
st.subheader('This app helps you extract and manage business card details efficiently.')
st.write(" 🧑‍💻 Tech Used: OCR, Streamlit GUI, SQL, Data Extraction")

select=option_menu(
    menu_title= None,
    options= ["About BizCard","Upload", "View & Edit", "Delete", "Process Followed"],
    icons=["house","cloud-upload","columns-gap", "trash","bounding-box"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

if select == "About BizCard":

  st.subheader(':red[About the App:]')
  st.write("BizCardX is a Streamlit web application designed for extracting information from business cards.") 
  st.write("It utilizes OCR (Optical Character Recognition) to extract text from uploaded images of business cards.") 
  st.write("The extracted details are then processed and organized into categories such as name, designation, contact information, company name, email, website, address, etc.") 
  st.write("Users can upload images of business cards, and the app extracts relevant information for storage and management.")
  st.subheader(":red[Technologies Used:]")
  st.write("The app is built using Python and several libraries, including Streamlit for the web interface, EasyOCR for optical character recognition, and MySQL for database operations.")
  st.write("The user interface is designed to be intuitive, allowing users to easily upload business card images, extract details, and manage the stored data.")

elif select == "Upload":

    image = st.file_uploader("Upload the image", type = ["png", "jpg", "jpeg"])

    if image is not None:
       
      st.image(image, width = 500)

      text_image, input_image = image_to_text(image)

      text_dic = extracted_text(text_image)
       
      if text_dic:
         st.success("Extraction Process Completed Successfully 👍")

      df = pd.DataFrame(text_dic)
       
      #Bytes conversion

      with open('K:\DS\BizCard\BizCard_1.png', 'rb') as f:
           photo = f.read()
      encodestring = base64.b64encode(photo)

      #Dictionary Creation

      data = {"Image": [encodestring]}

      df_1 = pd.DataFrame(data)

      concat = pd.concat([df, df_1], axis=1)

      st.dataframe(concat)

      button_1 = st.button("STORE THE INFORMATION :card_index_dividers: ")

      if button_1:
          
      #SQL Connection

        mydb = mysql.connector.connect(
            host = '', 
            user = '', 
            password = '', 
            database = '' 
         )
        mycursor = mydb.cursor()

      # SQL Table Creation

        mycursor.execute("create table if not exists bizcard_details(Name varchar(255), Designation varchar(255), Contacts varchar(255), Email varchar(255), Company_Name varchar(255), Website varchar(255), Address varchar(255), Pincode varchar(255), Image LONGBLOB)")
        data = concat.values.tolist()[0]
        mycursor.execute(("insert into bizcard_details(Name, Designation, Contacts, Email, Company_Name, Website, Address, Pincode, Image) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"),data)
        mydb.commit()

        st.success("Information Stored Successfully")


elif select == "View & Edit":                 
    selected_option = st.selectbox("Choose any one from below option", [ "View Data", "Edit Data"])
    if selected_option == "Select Below Options":
        pass
    
    elif selected_option == "View Data":
      mydb = mysql.connector.connect(
      host = '', 
      user = '', 
      password = '', 
      database = '' 
      )
      mycursor = mydb.cursor()
       
       #select query

      select_query = "select * from bizcard_details"

      mycursor.execute(select_query)

      table = mycursor.fetchall()

      mydb.commit()

      table_df = pd.DataFrame(table, columns=("Name", "Designation", "Contacts", "Email", "Company_Name", "Website", "Address", "Pincode", "Image"))
      st.dataframe(table_df)

    elif selected_option == "Edit Data":
       
       mydb = mysql.connector.connect(
       host = '', 
       user = '', 
       password = '', 
       database = '' 
       )
       mycursor = mydb.cursor()
       
       #select query

       select_query = "select * from bizcard_details"

       mycursor.execute(select_query)

       table = mycursor.fetchall()

       mydb.commit()

       table_df = pd.DataFrame(table, columns=("Name", "Designation", "Contacts", "Email", "Company_Name", "Website", "Address", "Pincode", "Image"))

       
       select_name = st.selectbox ("Select any Name", table_df["Name"])

       df_2 = table_df[table_df["Name"] == select_name]

       df_3 = df_2.copy()
       
       col1,col2 = st.columns(2)

       with col1: 
        modify_name = st.text_input("Name", df_2["Name"].unique()[0])
        modify_designation = st.text_input("Designation", df_2["Designation"].unique()[0])
        modify_contacts = st.text_input("Contacts", df_2["Contacts"].unique()[0])
        modify_address = st.text_input("Address", df_2["Address"].unique()[0])

        df_3["Name"] = modify_name 
        df_3["Designation"] = modify_designation 
        df_3["Contacts"] = modify_contacts
        df_3["Address"] = modify_address

       with col2:
        modify_company = st.text_input("Company_Name", df_2["Company_Name"].unique()[0])
        modify_email = st.text_input("Email", df_2["Email"].unique()[0])  
        modify_website = st.text_input("Website", df_2["Website"].unique()[0])
        modify_pincode = st.text_input("Pincode", df_2["Pincode"].unique()[0])

        df_3["Company_Name"] = modify_company   
        df_3["Email"] = modify_email 
        df_3["Website"] = modify_website
        df_3["Pincode"] = modify_pincode 

       modify_image = st.text_input("Image", df_2["Image"].unique()[0]) 
       df_3["Image"] = modify_image

       st.dataframe(df_3) 


       button_2 = st.button("SAVE THE CHANGES :arrows_counterclockwise:")

       if button_2:
         
        mydb = mysql.connector.connect(
        host = '', 
        user = '', 
        password = '', 
        database = '' 
        )
        mycursor = mydb.cursor()

        mycursor.execute(f"Delete from bizcard_details where Name = '{select_name}'")
        mydb.commit()

        data = df_3.values.tolist()[0]
        mycursor.execute(("insert into bizcard_details(Name, Designation, Contacts, Email, Company_Name, Website, Address, Pincode, Image) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"),data)
        mydb.commit()

        st.success("Information Changed Successfully")
  
elif select == "Delete":

    mydb = mysql.connector.connect(
    host = '', 
    user = '', 
    password = '', 
    database = '' 
    )
    mycursor = mydb.cursor()

    col1,col2 = st.columns(2)

    with col1:
      select_query_1 = "select Name from bizcard_details"

      mycursor.execute(select_query_1)

      table_1 = mycursor.fetchall()

      mydb.commit()

      del_name = []

      for i in table_1:
          del_name.append(i[0])
      
      name_selection = st.selectbox("Choose any Name from below:", del_name)

    with col2:
      select_query_2 = f"select Designation from bizcard_details where Name = '{name_selection}'"

      mycursor.execute(select_query_2)

      table_2 = mycursor.fetchall()

      mydb.commit()

      del_designation = []

      for i in table_2:
          del_designation.append(i[0])
      
      designation_selection = st.selectbox("Choose any Designation from below:", del_designation)
    
    if name_selection and designation_selection:
       
      col1,col2 = st.columns(2)

      with col1:
        st.write("")
        st.write(f"You have selected the Name: {name_selection}")
        st.write("")
        st.write("")
        remove = st.button("Move to Trash :recycle:")

        if remove:

          mycursor.execute(f"delete from bizcard_details where Name = '{name_selection}' and Designation = '{designation_selection}'") 
          mydb.commit()

          st.warning("Information move to Trash !!!")

      with col2:
        st.write("")
        st.write(f"You have selected the Designation: {designation_selection}")
        st.write("")        

elif select == "Process Followed":

    st.markdown("## :blue[Libraries Used]")
    st.markdown("###### 1. Streamlit - This import statement brings in the Streamlit package")
    st.markdown("###### 2. Streamlit option menu - The function is likely used to create an interactive menu within the Streamlit application, allowing users to navigate between different options or pages.")
    st.markdown("###### 3. Easyocr - This import statement brings in the easyocr package, which provides an easy-to-use optical character recognition (OCR) tool. It can be used to extract text from images.")
    st.markdown("###### 4. PIL - It allows you to work with images, including opening, processing, and displaying them.")
    st.markdown("###### 5. Pandas - This import statement brings in the pandas package, a powerful data manipulation and analysis library.")
    st.markdown("###### 6. numpy - This import statement brings in the numpy package, a numerical computing library that is commonly used for mathematical and scientific operations.")
    st.markdown("###### 7. Regular Expression - This import statement brings in the re module, which provides regular expression matching operations. It is useful for string pattern matching and manipulation.")
    st.markdown("###### 8. base64 - This is often used for encoding binary data, such as images, into a format suitable for transmission over networks.")
    st.markdown("###### 9. Input/Output - This io module, provides the ability to work with input and output (I/O) streams. These streams can represent various data sources such as files, strings, and other types of data buffers.")
    st.markdown("###### 10. MySQL Connector - It allows you to establish a connection to a MySQL database, execute queries, and perform other database operations.")
    st.markdown(" ")
    st.markdown("## :green[Feedback]")
    st.markdown("###### Kindly provide your valuable feedback for further developments")



# streamlit run BizCard.py
