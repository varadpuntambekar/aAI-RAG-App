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


# print(f"Working directory set to: {os.getcwd()}")




class navigation_pane(ctk.CTkScrollableFrame):
    def __init__(self, master, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = 'grey', border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.label = ctk.CTkLabel(self, text = "Navigation Pane", fg_color = 'grey', text_color= 'black')
        self.label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'ew')
        
        
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
    def __init__(self, master, width = 200, height = 200, corner_radius = None, border_width = None, bg_color = "transparent", fg_color = None, border_color = None, background_corner_colors = None, overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        #creating a new_chat button
        
        
        #creating a select folder for RAG button
        self.open_folder_btn = ctk.CTkButton(self, text = "Select Folder for RAG", hover_color='black', command= self.open_folder_click )
        self.open_folder_btn.grid(row = 0, column = 0, padx = (20,20), pady = (20,20), sticky = 'e')
       
       #Creating an input field to search and retrieve document:
        self.search_directory_input = ctk.CTkEntry(self, placeholder_text = "Which document would you like to speak with?", height = 50, font=("Arial", 18))
        self.search_directory_input.grid(row = 1, column = 0, columnspan = 2, padx = 0, pady = 10, sticky = 'ew')
        self.search_directory_input.bind("<Return>", self.submit_search_query_event)
        #Creating a submit search button
        self.search_dir_btn = ctk.CTkButton(self, text = 'Search', hover_color='black', command= self.submit_search_query)
        self.search_dir_btn.grid(row = 2, column = 0, padx = 0, pady = 10, sticky = 'e')

       #Creating s display window for search results
        self.search_results_display = ctk.CTkTextbox(self, bg_color= 'transparent', text_color= 'white', wrap='word', height=100, font=("Arial", 12))
        self.search_results_display.grid(row = 3, column = 0, padx = 20, pady = 20, columnspan = 2, sticky = 'nsew')
       
        #adding a page break
        self.page_break = ctk.CTkLabel(self, text = '', fg_color='grey', width = 10, height=10)
        self.page_break.grid(row = 4, column = 0, columnspan = 2, padx = (10,10), pady = (10,10), sticky = 'ew')

       #creating a enter user_input field
        self.input_field = ctk.CTkEntry(self, placeholder_text= "What would you like to ask the RAG?", font=("Arial", 18), height = 50)
        self.input_field.grid(row = 5, column = 0, padx = (40,20), pady = (20,20), sticky = 'ew', columnspan = 2)
        self.input_field.bind("<Return>", self.submit_ques_rag_event)
        
        #creating a text window to display text
        self.chat_display = ctk.CTkTextbox(self, bg_color='transparent', text_color='white', wrap = 'word', font=("Arial", 12) )
        self.chat_display.grid(row = 6, column = 0, columnspan = 2, padx = (40,40), pady = (20, 20), sticky = 'nsew')
        
        #creating a submit button
        self.submit_btn = ctk.CTkButton(self, text='Submit question', hover_color='black', command=self.submit_ques_rag)
        self.submit_btn.grid(row = 7, column = 0, padx = 20, pady = (0,40), sticky = 'e')
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        # self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight = 0)
        self.grid_rowconfigure(5, weight=0)
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
        self.search_results_display.insert("end", f"User search query: {search_query}\n")
        self.search_results_display.insert("end", f"The RAG retrieved the following document \n{self.get_relevant_doc(search_query)}\n")
        self.search_directory_input.delete(0,'end')

    def submit_search_query_event(self, event = None):
        self.submit_search_query()

    def get_relevant_doc(self, query):
        '''
        Input: A search query that the user asks
        Output: metadata['source'] i.e. the name of the document that was retrieved based on similarity score
        '''
        relevant_doc = ''
        retrieved_docs = self.embedder.retrieve_chunks(query, 3)
        for doc in retrieved_docs:
            relevant_doc += str(doc.metadata['source'])
            self.chat_history.append({"role": "Page Content", "content": doc.page_content})
        
        return relevant_doc

    
    
    def submit_ques_rag_event(self, event = None):
        self.submit_ques_rag()
    
    def open_folder_click(self):
        folder_selected = filedialog.askdirectory()
        self.directory_path = ctk.StringVar()
        if folder_selected:
            self.directory_path.set(folder_selected)
            self.selected_folder_path = self.directory_path.get()
            self.folder_absolute_path = os.path.abspath(self.selected_folder_path)
            logging.debug(f"the folder selected is {self.folder_absolute_path}")
        
        #create a ctklabel and display the name of the folder next to the button
            self.embedder = embed_search_retrieve(self.selected_folder_path)
            
            
            self.folder_path_label = ctk.CTkLabel(self, text=f"Selected Folder: {self.selected_folder_path[20:]}", fg_color='grey', text_color='blue')
            self.folder_path_label.grid(row = 0, column = 1, padx = (20,20), pady = (20,20), sticky = 'w')

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

    def submit_ques_rag(self):
        user_input = self.input_field.get()
        logging.debug(user_input)
        if user_input.lower() == 'exit':
            self.chat_display.insert("end", f"User: {user_input} \n")
            self.chat_display.insert("end", f"BOT: It was nice to chat with you, have a great day\n")
        
        self.chat_display.insert("end", f"User: {user_input}\n")
        self.chat_display.insert("end", f"BOT: {self.generate_response(user_input)}\n")
        


            # self.chat_display.insert("0.0", f"User: {user_input}\n")
            # self.chat_display.insert("end", f"BOT: {self.generate_response(user_input)}")

    def generate_response(self, user_input):
        '''
        function that stores chat history and formats the context and sends it to llm code to generate a response
        '''
        
        
        context = ''
        self.chat_history.append({"role": "user", "content": user_input})
        for msg in self.chat_history:
            context += f"{msg['role'].capitalize()} : {msg['content']}\n"
            logging.debug(context)
        ai_response = chat(user_input, context)
        self.chat_history.append({"role": "chatbot", "content": ai_response})
        return ai_response



    def embedding_in_thread(self):

        def update_progress(progress):
            self.new_window.after(0, lambda: self.embed_progress_bar.set(progress))
            
        def thread_target():
            self.embedder.load_and_embed_docs(update_progress= update_progress)

        threading.Thread(target=thread_target, daemon=True).start()


class chatbot(ctk.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        
        #define the geometry of the app
        self.geometry("600x500")
        self.title("CTK example")
        self.grid_columnconfigure(0,weight = 0) #width for the first column
        self.grid_columnconfigure(1, weight =1)
        self.grid_rowconfigure(0, weight=1) 

        #adding some widgets
        # self.button = ctk.CTkButton(self, text = "press me bitch", hover_color='black', command = self.button_click)
        # self.button.grid(row = 1,column = 1, sticky = 'ew', columnspan = 2, rowspan = 3)

        self.navigation = navigation_pane(master=self)
        self.navigation.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = 'ns')
    
        self.chat_frame = chat_frame(master = self)
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