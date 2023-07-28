import os

from itertools import count
from requests import get
from terminaltables import AsciiTable


def get_hh_vacancies(language, page, ):
    hh_url = "https://api.hh.ru/vacancies/"
    payload = {
        "text": language,
        "area": 1,
        "page": page,
    }

    response = get(hh_url, params=payload)
    response.raise_for_status()
    return response.json()


def get_superjob_vacancies(superjob_token,
                           page,
                           language):
    superjob_url = "https://api.superjob.ru/2.0/vacancies/"
    payload = {
        "town": "Moscow",
        "keyword": f"Программист {language}",
        "key": 48,
        "page": page,
    }
    headers = {"X-Api-App-Id": superjob_token}

    response = get(superjob_url,
                   params=payload,
                   headers=headers, )
    response.raise_for_status()
    vacancies = response.json()["objects"]
    return vacancies


def predict_rur_salary(salary_from,
                       salary_to,
                       need_currency,
                       salary_currency):
    if salary_currency != need_currency:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return None


def get_average_hh_pages(language, ):
    rur_vacancies = 0
    salary_sum = 0

    for page in count(0):
        if page > 99:
            break

        vacancies = get_hh_vacancies(language, page)

        for vacancy in vacancies["items"]:
            if not vacancy.get("salary"):
                continue

            salary = vacancy["salary"]
            predict_salary = predict_rur_salary(salary["from"],
                                                salary["to"],
                                                "RUR",
                                                salary["currency"], )
            if predict_salary is None:
                continue

            rur_vacancies += 1
            salary_sum += predict_salary

    languages_statistic = {
        "vacancies_found": vacancies["found"],
        "vacancies_processed": rur_vacancies,
        "average_salary": salary_sum / rur_vacancies,
    }
    return languages_statistic


def get_average_superjob_pages(language, superjob_token, ):
    vacancies_found = 0
    vacancies_processed = 0
    salary_sum = 0

    for page in range(0, 101):
        page_vacancies = get_superjob_vacancies(superjob_token,
                                                page,
                                                language, )

        for vacancy in page_vacancies:
            vacancies_found += 1
            salary = predict_rur_salary(
                vacancy["payment_from"],
                vacancy["payment_to"],
                "rub",
                vacancy["currency"],
            )
            if salary is None:
                continue

            vacancies_processed += 1
            salary_sum += salary
    superjob_statistic = {
        "language": language,
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": salary_sum / vacancies_processed,
    }

    return superjob_statistic


def print_table(languages_statistic, title, ):
    table_data = (
        ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата", ],
        ["JavaScript", languages_statistic["JavaScript"]["vacancies_found"],
         languages_statistic["JavaScript"]["vacancies_processed"],
         languages_statistic["JavaScript"]["average_salary"], ],
        ["C++", languages_statistic["C++"]["vacancies_found"], languages_statistic["C++"]["vacancies_processed"],
         languages_statistic["C++"]["average_salary"], ],
        ["Python", languages_statistic["Python"]["vacancies_found"],
         languages_statistic["Python"]["vacancies_processed"], languages_statistic["Python"]["average_salary"], ],
    )

    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[2] = "right"

    print(table_instance.table)
    print()


def main():
    superjob_token = os.environ["SUPERJOB_TOKEN"]
    languages = [
        "JavaScript",
        "C++",
        "Python",
    ]

    languages_hh_vacancies = {}

    for language in languages:
        languages_hh_vacancies[language] = get_average_hh_pages(language)

    print_table(languages_hh_vacancies, "HeadHunter")

    languages_superjob_vacancies = {}

    for language in languages:
        languages_superjob_vacancies[language] =
    get_average_superjob_pages(language, superjob_token)

    print_table(languages_superjob_vacancies)


if __name__ == "__main__":
    main()
