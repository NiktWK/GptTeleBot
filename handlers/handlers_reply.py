import requests, sys, os, uuid
sys.path.insert(1 , os.path.join(sys.path[0], '..'))
from handlers.handlers import *
from keyboards.keyboards import *
from states.states import CreateImage, Services
from config import *
@dp.message_handler(lambda message: message.text == generate_image.text)
async def create_image_r(message: types.Message, state: FSMContext ):
    await message.answer('Введите описание картинки (лучше на английском):')
    await state.set_state(CreateImage.prompt)

@dp.message_handler(state = CreateImage.prompt)
async def create_image_r(message: types.Message, state: FSMContext ):
    await state.finish()
    await get_image(message, True)

@dp.message_handler(lambda message: message.text == reset_b.text)
async def reset_r(message: types.Message, state: FSMContext):
    await reset(message, state)

@dp.message_handler(lambda message: message.text == settings.text)
async def settings_r(message: types.Message, state: FSMContext):
    await change(message)

@dp.message_handler(lambda message: message.text == help_b.text)
async def help_r(message: types.Message, state: FSMContext):
    await help(message, state)


# SERVICES
async def service_r(message: types.Message, text, state: FSMContext, next_state):
    await message.answer(text, reply_markup=back_reset_kb)
    await state.set_state(next_state)

async def service_text(message: types.Message, state: FSMContext, text, type_name):
    if message.text == back_r.text:
        await message.answer(servises.text, reply_markup=servises_kb)
        await state.set_state(Services.change)

    elif message.text == '/reset' or message.text == reset_b.text:
        s = """
            Здравствуйте! {}.
        """.format(text)

        GPT(str(message.from_user.id)).reset(type_name)
        await message.answer('*История сброшена*', 'Markdown')
        await message.answer(s, 'Markdown', reply_markup=back_reset_kb)

    elif message.text == '/help':
        await state.finish()
        await help(message, state)
    else:
        print("ТОЧКА 1")
        await global_tell(message, message.text, message.from_user.id, type_ = type_name, rm = back_reset_kb)


# POST
async def post_r(message: types.Message, state: FSMContext):
    await service_r(message, "Пришлите статью для поста", state, Services.Post.all_text)

@dp.message_handler(state = Services.Post.all_text)
async def post_text(message: types.Message, state: FSMContext):
    await service_text(message, state, "Пришлите статью для поста", "post")


# FORSTUDY
async def forstudy_r(message: types.Message, state: FSMContext):
    await service_r(message, "С какой темой вам помочь? Что вам не понятно?", state, Services.Study.all_text)

@dp.message_handler(state = Services.Study.all_text)
async def forstudy_text(message: types.Message, state: FSMContext):
    await service_text(message, state, "С какой темой вам помочь? Что вам не понятно?", "study")


# PROGRAMMING
async def programming_r(message: types.Message, state: FSMContext):
    text = "Укажите следующую информацию в вашем сообщении:\n  *1)* Язык програмимрования\n  *2)* Какие библиотеки/технологии использовать\n  *3)* Сама задача\n  *4)* Пример input-output"
    await service_r(message, text, state, Services.Programming.all_text)

@dp.message_handler(state = Services.Programming.all_text)
async def programming_text(message: types.Message, state: FSMContext):
    text = "Укажите следующую информацию в вашем сообщении:\n  *1)* Язык програмимрования\n  *2)* Какие библиотеки/технологии использовать\n  *3)* Сама задача\n  *4)* Пример input-output"
    await service_text(message, state, text, "programming")


# FORSTUDY
async def forstudy_r(message: types.Message, state: FSMContext):
    await service_r(message, "С какой темой вам помочь? Что вам не понятно?", state, Services.Study.all_text)

@dp.message_handler(state = Services.Study.all_text)
async def forstudy_text(message: types.Message, state: FSMContext):
    await service_text(message, state, "С какой темой вам помочь? Что вам не понятно?", "study")


@dp.message_handler(lambda message: message.text == servises.text)
async def services_r(message: types.Message, state: FSMContext):
    await message.answer('Что вы хотите сделать?', reply_markup=servises_kb)
    await state.set_state(Services.change)


@dp.message_handler(state = Services.change)
async def change_service_r(message: types.Message, state: FSMContext):
    text = message.text

    if text == back_r.text:
        await state.finish()
        await message.answer('Главное меню', reply_markup=base_kb)

    elif text == rewrite.text:
        #await rewrite_r(message, state)
        await state.finish()
        await message.answer('Главное меню', reply_markup=base_kb)

    elif text == forstudy.text:
        await forstudy_r(message, state)
        #await state.finish()
        #await message.answer('Главное меню', reply_markup=base_kb)

    elif text == post.text:
        await post_r(message, state)
        #await state.finish()
        #await message.answer('Главное меню', reply_markup=base_kb)

    elif text == programming.text:
        await programming_r(message, state)
        # await state.finish()
        # await message.answer('Главное меню', reply_markup=base_kb)

    else:
        await state.finish()
        await global_tell(message, message.text, message.from_user.id, rm = base_kb)


# # FORSTUDY (SERVICE)
# async def forstudy_r(message: types.Message, state: FSMContext):
#     await message.answer('С какой темой вам помочь? Что вам не понятно?', reply_markup=back_reset_kb)
#     await state.set_state(Services.Study.all_text)

# @dp.message_handler(state = Services.Study.all_text)
# async def forstudy_text(message: types.Message, state: FSMContext):

#     if message.text == back_r.text:
#         await message.answer(servises.text, reply_markup=servises_kb)
#         await state.set_state(Services.change)

#     elif message.text == '/reset' or message.text == reset_b.text:
#         s = """
#             Здравствуйте! С какой темой вам помочь? Что вам не понятно?
#         """
#         GPT(str(message.from_user.id)).reset('post')
#         await message.answer('*История сброшена*', 'Markdown')
#         await message.answer(s, reply_markup=back_reset_kb)
    
#     else:
#         await global_tell(message, message.text, message.from_user.id, type_ = 'study', rm = back_reset_kb)


# # REWRITE (SERVICE)
# async def rewrite_r(message: types.Message, state: FSMContext):
#     await message.answer('Пришлите текст для переписки', reply_markup=back_reset_kb)
#     await state.set_state(Services.Post.all_text)

# @dp.message_handler(state = Services.Rewrite.all_text)
# async def rewrite_text(message: types.Message, state: FSMContext):

#     if message.text == back_r.text:
#         await message.answer(servises.text, reply_markup=servises_kb)
#         await state.set_state(Services.change)
#     elif message.text == '/reset' or message.text == reset_b.text:
#         s = """
#             Здравствуйте! Пришлите текст для переписки.
#         """
#         GPT(str(message.from_user.id)).reset('post')
#         await message.answer('*История сброшена*', 'Markdown')
#         await message.answer(s, reply_markup=back_reset_kb)

#     elif message.text == '/help':
#         await state.finish()
#         await help(message, state)
#     else:
#         await global_tell(message, message.text, message.from_user.id, type_ = 'rewrite', rm = back_reset_kb)




