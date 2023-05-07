from aiogram.dispatcher.filters.state import State, StatesGroup

class NewAd(StatesGroup):
    header = State()
    text = State()
    image = State()
    shows = State()

class EditKey(StatesGroup):
    change_type = State()
    edit_openai = State()
    edit_diffusion = State()
    