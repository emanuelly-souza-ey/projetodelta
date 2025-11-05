from core.devops_service import (

    get_work_hours,

    get_project_status,

    get_overdue_tasks,

    get_daily_tasks

)

if __name__ == "__main__":

    project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e"

    print("Teste: Horas Semanais")

    get_work_hours(project_id, period="weekly")

    print("\nTeste: Horas Mensais")

    get_work_hours(project_id, period="monthly")

    print("\nTeste: Status do Projeto")

    print(get_project_status(project_id))

    print("\nTeste: Tarefas Atrasadas")

    print(get_overdue_tasks(project_id))

    print("\nTeste: Tarefas do Dia")

    print(get_daily_tasks(project_id)) 