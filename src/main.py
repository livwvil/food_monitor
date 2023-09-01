from peewee import *
from playhouse.db_url import connect
import configparser
import telebot
from datetime import datetime
import io
from telebot import apihelper
import sys

apihelper.ENABLE_MIDDLEWARE = True


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    bot_token = ''
    db_connection_string = ''
    if 'auth' in config:
        bot_token = config['auth']['bot_token']
        db_connection_string = config['auth']['db_connection_string']

    return bot_token, db_connection_string


(token, db_con_str) = read_config('conf.ini')


if len(sys.argv) > 1:
    db_con_str = db_con_str.replace("localhost", sys.argv[1])


db = connect(db_con_str)


class UserState:
    IDLE = 'idle'
    ADD_EATING = 'add_eating'
    ADD_ISSUE = 'add_issue'
    ADD_MEDICATION = 'add_medication'
    CLARIFY_EATING = 'clarify_eating'
    CLARIFY_ISSUE = 'clarify_issue'
    CLARIFY_MEDICATION = 'clarify_medication'
    FINISHING_ADD_EATING = 'finishing_add_eating'
    FINISHING_ADD_ISSUE = 'finishing_add_issue'
    FINISHING_ADD_MEDICATION = 'finishing_add_medication'


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField()
    state = TextField()
    chat_id = IntegerField()
    temporary = TextField()
    last_msg_id = TextField()

    def info(self):
        stash = str(self.temporary).replace('\n', ', ')
        return f"id: {self.id}\n" \
               f"state: {self.state}\n" \
               f"chat_id: {self.chat_id}\n" \
               f"temporary: {stash}\n" \
               f"last_msg_id: {self.last_msg_id}\n"


class Eating(BaseModel):
    id = IntegerField()
    user_id = ForeignKeyField(User, backref='eating')
    time = DateTimeField()


class Food(BaseModel):
    id = IntegerField()
    name = TextField()


class Eating2Food(BaseModel):
    id = IntegerField()
    eating_id = ForeignKeyField(Eating, backref='eating2food')
    food_id = ForeignKeyField(Food, backref='eating2food')


class Issue(BaseModel):
    id = IntegerField()
    user_id = ForeignKeyField(User, backref='issue')
    time = DateTimeField()


class Problem(BaseModel):
    id = IntegerField()
    name = TextField()


class Issue2Problem(BaseModel):
    id = IntegerField()
    issue_id = ForeignKeyField(Issue, backref='issue2problem')
    problem_id = ForeignKeyField(Problem, backref='issue2problem')


class Medication(BaseModel):
    id = IntegerField()
    user_id = ForeignKeyField(User, backref='medication')
    time = DateTimeField()


class Medicine(BaseModel):
    id = IntegerField()
    name = TextField()


class Medication2Medicine(BaseModel):
    id = IntegerField()
    medication_id = ForeignKeyField(Medication, backref='medication2medicine')
    medicine_id = ForeignKeyField(Medicine, backref='medication2medicine')


def insert_user(chat_id, state):
    user = User(chat_id=chat_id, state=state)
    if user.save():
        return user
    else:
        return None


def get_user_by_chat_id(chat_id):
    some = User.select().where(User.chat_id == chat_id)
    if some:
        return some.get()
    else:
        return None


# def delete_user_by_chat_id(chat_id):
#     some = User.select().where(User.chat_id == chat_id)
#     if some:
#         return some.get().delete_instance()
#     else:
#         return None


def get_user(chat_id):
    user = get_user_by_chat_id(chat_id)
    if user is None:
        user = insert_user(chat_id, UserState.IDLE)
    return user


datetime_pattern = "%d.%m.%Y %H:%M"


def add_eating(dt, food, user):
    cur_eating = Eating(user_id=user.id, time=datetime.strptime(dt, datetime_pattern))
    cur_eating.save()
    for cur_item in food:
        db_item = Food.select().where(Food.name == cur_item)
        if db_item:
            db_item = db_item.get()
        else:
            db_item = Food(name=cur_item)
            db_item.save()
        cur_e2f = Eating2Food(eating_id=cur_eating.id, food_id=db_item.id)
        cur_e2f.save()


def add_issue(dt, problems, user):
    cur_issue = Issue(user_id=user.id, time=datetime.strptime(dt, datetime_pattern))
    cur_issue.save()
    for cur_item in problems:
        db_item = Problem.select().where(Problem.name == cur_item)
        if db_item:
            db_item = db_item.get()
        else:
            db_item = Problem(name=cur_item)
            db_item.save()
        cur_i2p = Issue2Problem(issue_id=cur_issue.id, problem_id=db_item.id)
        cur_i2p.save()


def add_medication(dt, medicines, user):
    cur_medication = Medication(user_id=user.id, time=datetime.strptime(dt, datetime_pattern))
    cur_medication.save()
    for cur_item in medicines:
        db_item = Medicine.select().where(Medicine.name == cur_item)
        if db_item:
            db_item = db_item.get()
        else:
            db_item = Medicine(name=cur_item)
            db_item.save()
        cur_m2m = Medication2Medicine(medication_id=cur_medication.id, medicine_id=db_item.id)
        cur_m2m.save()


def get_statistics(user):
    stats = {}
    f = list(Eating.select(Eating.time, Food.name).join(Eating2Food).join(Food).where(Eating.user_id == user.id).dicts())
    p = list(Issue.select(Issue.time, Problem.name).join(Issue2Problem).join(Problem).where(Issue.user_id == user.id).dicts())
    m = list(Medication.select(Medication.time, Medicine.name).join(Medication2Medicine).join(Medicine).where(Medication.user_id == user.id).dicts())
    for row in [*f, *p, *m]:
        [date_str, time_str] = row['time'].strftime(datetime_pattern).split(" ")
        if date_str not in stats:
            stats[date_str] = {time_str: [row['name']]}
        else:
            if time_str not in stats[date_str]:
                stats[date_str][time_str] = [row['name']]
            else:
                stats[date_str][time_str].append(row['name'])
    result = ""
    for key_d in reversed(sorted(list(stats.keys()), key=lambda date: datetime.strptime(date, datetime_pattern.split(" ")[0]))):
        result += key_d + "\n"
        for key_t in reversed(sorted(list(stats[key_d].keys()))):
            result += "\t" + key_t + "\n\t\t- " + "\n\t\t- ".join(stats[key_d][key_t]) + "\n"
    return result


def transform_datetime(datetime_str, pattern):
    try:
        dt = datetime.strptime(datetime_str, pattern)
    except Exception:
        try:
            now = datetime.now()
            dt_str = ".".join([str(now.day), str(now.month), str(now.year)]) + " " + datetime_str
            dt = datetime.strptime(dt_str, pattern)
        except Exception:
            dt = datetime.now()
    return dt.strftime(pattern)


print_dbg_info = True


def dbg_merge(before, after):
    b = before.split("\n")
    a = after.split("\n")
    result = ""
    for i in range(len(b)):
        if b[i] != a[i]:
            prop = b[i][0:b[i].index(":")]
            b_val = b[i][b[i].index(":") + 2:]
            a_val = a[i][a[i].index(":") + 2:]
            result += prop + "\t" + b_val + " ---> " + a_val + "\n"
    return result


def run_bot(bot_token):
    print('bot runs\ntocken: ' + bot_token)
    bot = telebot.TeleBot(bot_token)

    @bot.middleware_handler(update_types=['message'])
    def middleware(bot_instance, message):
        pass

    def delete_last_msg_with_keyboard(cid):
        user = get_user(cid)
        if user.last_msg_id is not None:
            [cid, mid] = str(user.last_msg_id).split(";")
            try:
                bot.delete_message(cid, mid)
            except Exception:
                pass
            user.last_msg_id = None
            user.save()

    def save_last_msg_with_keyboard(user, msg):
        delete_last_msg_with_keyboard(msg.chat.id)
        user.last_msg_id = str(msg.chat.id) + ";" + str(msg.id)
        user.save()

    def reset_user_state(user):
        user.state = UserState.IDLE
        user.temporary = None
        user.save()
        delete_last_msg_with_keyboard(user.chat_id)

    def get_reset_user(cid):
        user = get_user(cid)
        reset_user_state(user)
        return user

    @bot.message_handler(commands=['start', 'help'])
    def start_command(message):
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        get_reset_user(message.chat.id)
        bot.send_message(message.chat.id, "Print /af to add food, /ap to add problem or /st to get statistics")

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    @bot.message_handler(commands=['st'])
    def statistics_command(message):
        user = get_reset_user(message.chat.id)
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        statistics = get_statistics(user)
        file = io.StringIO(statistics)
        if statistics != "":
            bot.send_document(message.chat.id, file, visible_file_name="stats.txt")
        else:
            bot.send_message(message.chat.id, "No statistics yet")

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))
            print(statistics)

    @bot.message_handler(commands=['ai'])
    def ai_command(message):
        user = get_reset_user(message.chat.id)
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        user.state = UserState.ADD_ISSUE
        user.save()
        msg = bot.send_message(message.chat.id, 'What problem you would like to add?',
                               reply_markup=telebot.types.InlineKeyboardMarkup([
                                   [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                               ]))
        save_last_msg_with_keyboard(user, msg)

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    @bot.message_handler(commands=['ae'])
    def ae_command(message):
        user = get_reset_user(message.chat.id)
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        user.state = UserState.ADD_EATING
        user.save()
        msg = bot.send_message(message.chat.id, 'What food you would like to add?',
                               reply_markup=telebot.types.InlineKeyboardMarkup([
                                   [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                               ]))
        save_last_msg_with_keyboard(user, msg)

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    @bot.message_handler(commands=['am'])
    def am_command(message):
        user = get_reset_user(message.chat.id)
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        user.state = UserState.ADD_MEDICATION
        user.save()
        msg = bot.send_message(message.chat.id, 'What medicine you would like to add?',
                               reply_markup=telebot.types.InlineKeyboardMarkup([
                                   [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                               ]))
        save_last_msg_with_keyboard(user, msg)

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    def item_typing_handler(message, user):
        delete_last_msg_with_keyboard(message.chat.id)

        existing_items = []
        if user.state in [UserState.ADD_EATING, UserState.CLARIFY_EATING]:
            user.state = UserState.CLARIFY_EATING
            existing_items = [it.name.lower() for it in Food.select()]
        if user.state in [UserState.ADD_ISSUE, UserState.CLARIFY_ISSUE]:
            user.state = UserState.CLARIFY_ISSUE
            existing_items = [it.name.lower() for it in Problem.select()]
        if user.state in [UserState.ADD_MEDICATION, UserState.CLARIFY_MEDICATION]:
            user.state = UserState.CLARIFY_MEDICATION
            existing_items = [it.name.lower() for it in Medicine.select()]

        user.save()

        typed_item = message.text.lower().strip()
        advise_items = list(filter(lambda it: typed_item in it or it in typed_item, existing_items))

        keys_with_existing_items = []
        for item in advise_items:
            keys_with_existing_items.append(
                [telebot.types.InlineKeyboardButton(text='Existing: ' + item, callback_data=item)])

        msg = bot.send_message(message.chat.id, text="Select or type again",
                               reply_markup=telebot.types.InlineKeyboardMarkup([
                                   *keys_with_existing_items,
                                   [telebot.types.InlineKeyboardButton(text='Literally: ' + typed_item,
                                                                       callback_data=typed_item)],
                                   [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                               ]))
        save_last_msg_with_keyboard(user, msg)

    def datetime_typing_handler(message, user):
        dt = transform_datetime(message.text, datetime_pattern)
        msg = bot.send_message(message.chat.id, text="Select or type again",
                               reply_markup=telebot.types.InlineKeyboardMarkup([
                                   [telebot.types.InlineKeyboardButton(text=dt, callback_data=dt)],
                                   [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                               ]))
        save_last_msg_with_keyboard(user, msg)

    text_request_handlers = {
        UserState.ADD_EATING: item_typing_handler,
        UserState.CLARIFY_EATING: item_typing_handler,
        UserState.FINISHING_ADD_EATING: datetime_typing_handler,
        UserState.ADD_ISSUE: item_typing_handler,
        UserState.CLARIFY_ISSUE: item_typing_handler,
        UserState.FINISHING_ADD_ISSUE: datetime_typing_handler,
        UserState.ADD_MEDICATION: item_typing_handler,
        UserState.CLARIFY_MEDICATION: item_typing_handler,
        UserState.FINISHING_ADD_MEDICATION: datetime_typing_handler
    }

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        user = get_user(message.chat.id)
        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            dbg_before = dbg_user.info()

        state = str(user.state)
        if state in text_request_handlers:
            handler = text_request_handlers[state]
            handler(message, user)
        else:
            bot.send_message(message.chat.id, text="Dont understand")

        if print_dbg_info:
            dbg_user = get_user(message.chat.id)
            print(message.text + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    def abort_if_requested(user, msg):
        if msg == 'aborting':
            reset_user_state(user)
            bot.send_message(user.chat_id, 'Aborted!')
        return msg == 'aborting'

    @bot.callback_query_handler(
        func=lambda call: get_user(call.message.chat.id).state in [UserState.ADD_EATING, UserState.ADD_ISSUE, UserState.ADD_MEDICATION])
    def continue_adding_callback_worker(call):
        cid = call.message.chat.id
        user = get_user(cid)
        if print_dbg_info:
            dbg_user = get_user(cid)
            dbg_before = dbg_user.info()

        if not abort_if_requested(user, call.data):
            delete_last_msg_with_keyboard(cid)

            if call.data == 'finishing':
                if user.state == UserState.ADD_EATING:
                    user.state = UserState.FINISHING_ADD_EATING
                    user.save()
                if user.state == UserState.ADD_ISSUE:
                    user.state = UserState.FINISHING_ADD_ISSUE
                    user.save()
                if user.state == UserState.ADD_MEDICATION:
                    user.state = UserState.FINISHING_ADD_MEDICATION
                    user.save()

                msg = bot.send_message(cid, 'Define time <dd.mm.yyyy HH:MM> or <HH:MM>',
                                       reply_markup=telebot.types.InlineKeyboardMarkup([
                                           [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
                                       ]))
                save_last_msg_with_keyboard(user, msg)

        if print_dbg_info:
            dbg_user = get_user(cid)
            print(call.data + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    def save_input_to_stash(user, food):
        tmp = user.temporary
        if tmp is None:
            tmp = food
        else:
            tmp += "\n" + food
        user.temporary = tmp
        user.save()

    @bot.callback_query_handler(
        func=lambda call: get_user(call.message.chat.id).state in [UserState.CLARIFY_EATING, UserState.CLARIFY_ISSUE, UserState.CLARIFY_MEDICATION])
    def clarify_input_callback_worker(call):
        cid = call.message.chat.id
        user = get_user(cid)
        if print_dbg_info:
            dbg_user = get_user(cid)
            dbg_before = dbg_user.info()

        if not abort_if_requested(user, call.data):
            delete_last_msg_with_keyboard(cid)

            save_input_to_stash(user, call.data)
            bot.send_message(cid, call.data + ' added')

            if user.state == UserState.CLARIFY_EATING:
                user.state = UserState.ADD_EATING
                user.save()
            if user.state == UserState.CLARIFY_ISSUE:
                user.state = UserState.ADD_ISSUE
                user.save()
            if user.state == UserState.CLARIFY_MEDICATION:
                user.state = UserState.ADD_MEDICATION
                user.save()

            msg = bot.send_message(cid, text="Anything else?", reply_markup=telebot.types.InlineKeyboardMarkup([
                [telebot.types.InlineKeyboardButton(text='Finish and add time', callback_data='finishing')],
                [telebot.types.InlineKeyboardButton(text='Abort', callback_data='aborting')]
            ]))
            save_last_msg_with_keyboard(user, msg)

        if print_dbg_info:
            dbg_user = get_user(cid)
            print(call.data + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    @bot.callback_query_handler(func=lambda call: get_user(call.message.chat.id).state in [UserState.FINISHING_ADD_EATING,
                                                                                           UserState.FINISHING_ADD_ISSUE,
                                                                                           UserState.FINISHING_ADD_MEDICATION])
    def finishing_adding_callback_worker(call):
        cid = call.message.chat.id
        user = get_user(cid)
        if print_dbg_info:
            dbg_user = get_user(cid)
            dbg_before = dbg_user.info()

        if not abort_if_requested(user, call.data):
            delete_last_msg_with_keyboard(cid)

            stash = str(user.temporary).split("\n")
            dt = call.data

            if user.state == UserState.FINISHING_ADD_EATING:
                add_eating(dt, stash, user)
            if user.state == UserState.FINISHING_ADD_ISSUE:
                add_issue(dt, stash, user)
            if user.state == UserState.FINISHING_ADD_MEDICATION:
                add_medication(dt, stash, user)

            reset_user_state(user)
            bot.send_message(cid, "Saved:\n" + ", ".join(stash) + "\nat " + dt)

        if print_dbg_info:
            dbg_user = get_user(cid)
            print(call.data + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        cid = call.message.chat.id
        user = get_user(cid)
        if print_dbg_info:
            dbg_user = get_user(cid)
            dbg_before = dbg_user.info()

        if not abort_if_requested(user, call.data):
            cid = call.message.chat.id
            delete_last_msg_with_keyboard(cid)
            bot.send_message(call.message.chat.id, 'Dont understand')

        if print_dbg_info:
            dbg_user = get_user(cid)
            print(call.data + "\n" + dbg_merge(dbg_before, dbg_user.info()))

    bot.polling()


if __name__ == '__main__':
    if token != '':
        db.connect()
        run_bot(token)
        db.close()
    else:
        print('bot token not found')
