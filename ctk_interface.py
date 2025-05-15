import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from chatbot import chat, embed_search_retrieve
import threading
import pydantic.deprecated.decorator
import opentelemetry.context.contextvars_context
import os
import sys
import logging
from PIL import Image
import io

# print(f"Working directory set to: {os.getcwd()}")




class navigation_pane(ctk.CTkScrollableFrame):
    def __init__(self, master, parent, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = 'grey', border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.label = ctk.CTkLabel(self, text = "Navigation Pane", fg_color = 'grey', text_color= 'black')
        self.label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'ew')
        
        self.parent = parent #telling that the parent is the chatbot class which is the main class

        self.new_chat_index = 0

        
        self.new_chat_btn = ctk.CTkButton(self, text = "Create New Chat", hover=True, hover_color='black', command=self.create_new_chat)
        self.new_chat_btn.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'w')



    def create_new_chat(self):
        
        button_text = f"Chat_{self.new_chat_index + 1}"
        self.chat_btn = ctk.CTkButton(self, text = button_text, hover_color="black")
        self.chat_btn.grid(row = self.new_chat_index + 1, column = 0, padx = 10, pady = 10, sticky = 'ew')
        self.new_chat_index += 1
        # self.button_chat_2 = ctk.CTkButton(self, text = "Chat_2", hover_color="black")
        # self.button_chat_2.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = 'w')


        # self.grid_columnconfigure(0, weight= 1)
        # self.grid_rowconfigure(1, weight = 1)
        # self.grid_rowconfigure(2, weight = 1)


class chat_frame(ctk.CTkScrollableFrame):
    def __init__(self, master, parent, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = None, border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        #creating a new_chat button
        
        self.parent = parent
        
        #creating a select folder for RAG button
        self.open_folder_btn = ctk.CTkButton(self, text = "Select Folder for RAG", hover_color='black', command= self.open_folder_click )
        self.open_folder_btn.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'w')

        #creating a select file button to upload a single file
        self.open_file_btn = ctk.CTkButton(self, text = "Select File for RAG", hover_color='black', command= self.open_file_click )
        self.open_file_btn.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'e')

       
       #Creating an input field to search and retrieve document:
        self.search_directory_input = ctk.CTkEntry(self, placeholder_text = "Ask me anything, I will search the appropriate files and give a summary", height = 50, font=("Arial", 18))
        self.search_directory_input.grid(row = 1, column = 0, columnspan = 1, padx = 20, pady = 10, sticky = 'ew')
        self.search_directory_input.bind("<Return>", self.submit_search_query_event)
        #Creating a submit search button
        self.search_dir_btn = ctk.CTkButton(self, text = 'Search', hover_color='black', command= self.submit_search_query)
        self.search_dir_btn.grid(row = 2, column = 0, padx = 20, pady = 10, sticky = '')

       #Creating s display window for search results (Edit 02 May 2025, we don't really need this we are making it just one thing)
        # self.search_results_display = ctk.CTkTextbox(self, bg_color= 'transparent', text_color= 'white', wrap='word', height=100, font=("Arial", 12))
        # self.search_results_display.grid(row = 3, column = 0, padx = 20, pady = 20, columnspan = 1, sticky = 'nsew')
        # self.search_results_display.configure(font= ("Arial", 12))
        
        
        #adding a page break (2nd May, dont need this anymore either, just one textbox that displays all the results)
        # self.horz_page_break = ctk.CTkLabel(self, text = '', fg_color='grey', width = 10, height=10)
        # self.horz_page_break.grid(row = 4, column = 0, columnspan = 1, padx = (10,10), pady = (10,10), sticky = 'ew')

        #adding a vertical page break
        self.vert_page_break = ctk.CTkLabel(self, text = '', fg_color='grey', width = 10, height=10)
        self.vert_page_break.grid(row = 1, column = 1, rowspan = 9,   padx = (30,10), pady = (10,10), sticky = 'ens')

       #creating a enter user_input field
        self.input_field = ctk.CTkEntry(self, placeholder_text= "Do you have any follow up questions?", font=("Arial", 18), height = 50)
        self.input_field.grid(row = 6, column = 0, padx = (40,20), pady = (20,20), sticky = 'ew', columnspan = 1)
        self.input_field.bind("<Return>", self.submit_ques_rag_event)
        
        #creating a text window to display text
        self.chat_display = ctk.CTkTextbox(self, bg_color='transparent', text_color='white', wrap = 'word', font=("Arial", 12), height = 400 )
        self.chat_display.grid(row = 5, column = 0, columnspan = 1, padx = (40,20), pady = (20, 20), sticky = 'nsew')
        self.chat_display.configure(font = ("Arial", 12))
        #Creating a radiobutton for either qa or summarisation task
        # self.selected_task = ctk.StringVar(value='summarise')
        # self.sum_task_spec = ctk.CTkRadioButton(self, bg_color='transparent', text_color='white', text = 'Summarisation', variable=self.selected_task, font=("Arial", 12)  )
        # self.sum_task_spec.grid(row = 7, column = 0, padx = 20, pady = 10, sticky = 'w')

        # self.qa_task_spec = ctk.CTkRadioButton(self, bg_color='transparent', text_color='white', text = 'Question Answering', variable=self.selected_task, font=("Arial", 12)  )
        # self.qa_task_spec.grid(row = 8, column = 0, padx = 20, pady = 10, sticky = 'w')

        #creating a submit button
        self.submit_btn = ctk.CTkButton(self, text='Submit question', hover_color='black', command=self.submit_ques_rag)
        self.submit_btn.grid(row = 7, column = 0, padx = 20, pady = (0,40), sticky ='' )
        
        

        #Creating a new frame on the right hand side that is essentially a pdf viewer with highlights
        #DO NOT Change the Rowspan on this, extrmely important
        self.pdf_viewer_frame = ctk.CTkScrollableFrame(master=self)
        self.pdf_viewer_frame.grid(row = 1,column = 2, rowspan = 9, padx = 0, pady = 0, sticky = 'nsew')
        
        #Displaying a label that tells that this section displays images of pdfs
        self.display_pdf_btn = ctk.CTkButton(self, text = "Display Image from retrieved Doc"  )
        self.display_pdf_btn.grid(row = 0, column = 2, padx = (20,20), pady = (20,20), sticky = '')
        
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight = 0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        self.grid_rowconfigure(7, weight = 0)
        self.grid_rowconfigure(8, weight=0)
        
        #Storing the chat history
        self.chat_history = []
        
        #creating a directory path variable
        self.directory_path = None

        self.embedder = None
    
    def submit_search_query(self):
        '''
        Input: A search query that the user inputs
        Output: Display of a result
        '''
        search_query = self.search_directory_input.get()
        logging.debug(search_query)
        # self.chat_display.insert("end", f"User search query: {search_query}\n")
        self.chat_display.insert("end", f"The RAG retrieved the following document \n{self.get_relevant_doc(search_query)}\n")
        self.search_directory_input.delete(0,'end')

    def submit_search_query_event(self, event = None):
        self.submit_search_query()

    def get_relevant_doc(self, query):
        '''
        Input: A search query that the user asks
        Output: metadata['source'] i.e. the name of the document that was retrieved based on similarity score
        '''
        relevant_doc = ''
        retrieved_docs, retrieved_img = self.embedder.retrieve_chunks(query, 3)
        #Display only the source of the first chunk, assuming that all other chunks will be from the same document.
        relevant_doc = str(retrieved_docs[0].metadata['source'])
        
        for doc in retrieved_docs:    
            self.chat_history.append({"role": "Page Content", "content": doc.page_content})
        
        pix = retrieved_img.get_pixmap(annots = True)
        img_data = pix.tobytes('png')

        self.folder_display = ctk.CTkTextbox(self.pdf_viewer_frame, height = 50, bg_color='transparent', text_color='white', wrap = 'word', font=("Arial", 12) )
        self.folder_display.grid(row = 0, column = 0, columnspan = 2, padx = (20,20), pady = (20, 20), sticky = 'nsew')
        self.folder_display.insert("end", f"Retrieved doc is {relevant_doc[20:]}")

        img = Image.open(io.BytesIO(img_data))

        img_to_display = ctk.CTkImage(light_image= img, dark_image= img, size = (600, 800))
        
        self.annot_page_display = ctk.CTkLabel(master = self.pdf_viewer_frame, text = '')
        self.annot_page_display.grid(row = 1, column = 0 ,padx = 20, pady = 20, sticky = 'nsew')
        self.annot_page_display.configure(image = img_to_display)
        self.annot_page_display.image = img_to_display

        #When the first call is made to ask the retrieve the chunks from the document, 
        self.generate_response ( query, task = 'summarise')

        return relevant_doc

    
    
    def submit_ques_rag_event(self, event = None):
        self.submit_ques_rag()
    
    def open_folder_click(self):
        folder_selected = filedialog.askdirectory()
        #declare the variable
        self.directory_path = ctk.StringVar()
        if folder_selected:
            #set the variable
            self.directory_path.set(folder_selected)
            #modify the variable to get the string value
            self.selected_folder_path = self.directory_path.get()
            #get the absolute path
            self.folder_absolute_path = os.path.abspath(self.selected_folder_path)
            logging.debug(f"the folder selected is {self.folder_absolute_path}")
        
        #create a ctklabel and display the name of the folder next to the button
            self.embedder = embed_search_retrieve(self.selected_folder_path)
            
            
            self.folder_path_label = ctk.CTkLabel(self, text=f"Folder Selected Successfully", fg_color='blue', text_color='white')
            self.folder_path_label.grid(row = 0, column = 0, padx = (10,10), pady = (20,20), sticky = '')

        #This function also starts the embedding process
        #Creates a new_window that shows progress bar for embedding
            self.new_window = ctk.CTkToplevel(self)
            self.new_window.title("Embedding_files_progress")
            self.new_window.geometry("400x200")
            self.new_window_label = ctk.CTkLabel(self.new_window, text=f"Embedding Files from {self.directory_path.get()} ")
            self.new_window_label.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'e')
            #Create a progress bar and display it
            self.embed_progress_bar = ctk.CTkProgressBar(self.new_window, width=200)
            self.embed_progress_bar.set(0)
            self.embed_progress_bar.grid(row = 1, column = 0, padx = (20,20), pady = (20,20), sticky = "ew")

            #start the embedding progress
            self.embedding_in_thread()
    
    
        
        return self.directory_path
    
    def open_file_click(self):
        file_selected = filedialog.askopenfilename()
        self.filepath = ctk.StringVar()
        if file_selected:
            self.filepath.set(file_selected)
            selected_filepath = self.filepath.get()
            selected_file_abspath = os.path.abspath(selected_filepath)
            logging.debug(f"=============Selected file in {selected_file_abspath}================")
            selected_subdirectory_abspath = os.path.dirname(selected_file_abspath)

            self.embedder = embed_search_retrieve(selected_subdirectory_abspath, filepath=self.filepath)
            
            self.folder_path_label = ctk.CTkLabel(self, text=f"File Selected Successfully", fg_color='blue', text_color='white')
            self.folder_path_label.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'e')

        #This function also starts the embedding process
        #Creates a new_window that shows progress bar for embedding
            self.new_window = ctk.CTkToplevel(self)
            self.new_window.title("Embedding_files_progress")
            self.new_window.geometry("400x200")
            self.new_window_label = ctk.CTkLabel(self.new_window, text=f"Embedding File Selected ")
            self.new_window_label.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'e')
            #Create a progress bar and display it
            self.embed_progress_bar = ctk.CTkProgressBar(self.new_window, width=200)
            self.embed_progress_bar.set(0)
            self.embed_progress_bar.grid(row = 1, column = 0, padx = (20,20), pady = (20,20), sticky = "ew")

            #start the embedding progress
            self.embedding_in_thread()

            

    def submit_ques_rag(self):
        user_input = self.input_field.get()
        logging.debug(user_input)
        if user_input.lower() == 'exit':
            self.chat_display.insert("end", f"User: {user_input} \n\n" ,"bold")
            self.chat_display.insert("end", f"BOT: It was nice to chat with you, have a great day\n")
        
        self.chat_display.insert("end", f"User: {user_input}\n\n", "bold")
        self.generate_response(user_input)
        # self.chat_display.insert("end", f"BOT: {self.generate_response(user_input)}\n")
        


            # self.chat_display.insert("0.0", f"User: {user_input}\n")
            # self.chat_display.insert("end", f"BOT: {self.generate_response(user_input)}")

    def generate_response(self, user_input, task = 'qa'):
        '''
        function that stores chat history and formats the context and sends it to llm code to generate a response
        '''
        
        
        context = ''
        self.chat_history.append({"role": "user", "content": user_input})
        for msg in self.chat_history:
            context += f"{msg['role'].capitalize()} : {msg['content']}\n"
            logging.debug(context)
        
        #add a progress bar on top of the Textbox to show user that answer is being generated.
        
        #create a threaded llm_call function to call the llm in a separate thread
        logging.debug(f"Calling LLM now")
        threading.Thread(target=self.threaded_llm_call, args=(user_input, context, task), daemon = True).start()



    def embedding_in_thread(self):

        def update_progress(progress):
            self.new_window.after(0, lambda: self.embed_progress_bar.set(progress))
            
        def thread_target():
            self.embedder.load_and_embed_docs(update_progress= update_progress)

        threading.Thread(target=thread_target, daemon=True).start()

    
    def threaded_llm_call(self, user_input, context, task):
        '''
        Creates a separate function in which the LLM is called, this is so that this function can be threaded easily.
        '''
        logging.debug(f"Inside the threaded function now")
        response = chat(user_input, context, task) #the chat function is from the chatbot.py script
        logging.debug(f"The LLM has created a response, but the response is not visible")
        self.chat_display.insert("end", f"BOT: {response}\n")
        logging.debug(f"The llm has responded and the response shown")




class chatbot(ctk.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        
        #define the geometry of the app
        self.geometry("600x500")
        self.title("CTK example")
        self.grid_columnconfigure(0,weight = 0) #width for the first column
        self.grid_columnconfigure(1, weight =1)
        self.grid_rowconfigure(0, weight=1) 


        #Storing Chat history
        self.chat_sessions = [] #stores all previous chat_sessions
        self.current_chat = [] #stores current chat


        #adding some widgets
        # self.button = ctk.CTkButton(self, text = "press me bitch", hover_color='black', command = self.button_click)
        # self.button.grid(row = 1,column = 1, sticky = 'ew', columnspan = 2, rowspan = 3)

        self.navigation = navigation_pane(master=self, parent = self)
        self.navigation.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = 'ns')
    
        self.chat_frame = chat_frame(master = self, parent = self)
        self.chat_frame.grid(row = 0, column = 1, sticky = 'nsew')

    
    
        #adding a tabview
        # tabview = ctk.CTkTabview(master=self)
        # tabview.grid(row = 3, column = 3, padx = 20, pady = 20)
        # tabview.add("chat1")
        # tabview.add("chat2")
        # tabview.add("chat3")
        # tabview.set("chat1")

    #add an event listener
    def button_click(self):
        counter = 0
        logging.debug(f"button clicked {counter} times")
        counter += 1

def get_application_path():
    # When running as script
    if getattr(sys, 'frozen', False):
        # When running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # When running as .py script
        return os.path.dirname(os.path.abspath(__file__))

# Set the working directory



if __name__ == "__main__":
    
    
    #creating a log file , very important to print out statements if I cannot do a 
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app-debug.log")
    logging.basicConfig(
    filename="print_log",
    filemode='w',
    level = logging.DEBUG,
    format = '%(asctime)s - %(levelname)s - %(message)s '
)

    logging.debug("App Started")
    
    application_path = get_application_path()
    os.chdir(application_path)
    logging.debug(application_path)

    app = chatbot()
    app.mainloop()