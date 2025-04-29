from handlers import buttons_handler, command_handler, files_handler, tasks_handler

def get_routers():
    routers = []
    for handler in [buttons_handler, command_handler, files_handler, tasks_handler]:
        routers.append(handler.router)
    return routers