import LV1, LV2
import start_menu

levels = [LV1, LV2]

while True:
    selected_level = start_menu.main()
    if selected_level == "exit":
        break
    print(selected_level)

    levels[selected_level-1].main()


