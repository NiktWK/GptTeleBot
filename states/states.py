from aiogram.dispatcher.filters.state import State, StatesGroup

class EditKey(StatesGroup):
    change_type = State()
    edit_openai = State()
    edit_diffusion = State()
    
class EditParameters(StatesGroup):
    keywords = State()
    answer_type = State()
    answer_voice_chat = State()
    save_history = State()

class Mailing(StatesGroup):
    text = State()
    image = State()
    goal_auditory = State()
    check_result = State()

class AD(Mailing):
    max_shows = State()

class Services(StatesGroup):
    change = State()
    
    class Post(StatesGroup):
        all_text = State()
    
    class Study(StatesGroup):
        all_text = State()

    class Rewrite(StatesGroup):
        all_text = State()

    class Programming(StatesGroup):
        all_text = State()
        
class CreateImage(StatesGroup):
    prompt = State()

