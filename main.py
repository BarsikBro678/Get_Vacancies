from itertools import count
import os

from requests import get
from terminaltables import AsciiTable


def get_hh_vacancies(language, page,):
	hh_url = "https://api.hh.ru/vacancies/"
	moscow_hh_id = 1
	payload = {
		"text": language,
		"area": moscow_hh_id,
		"page": page,
	}
	
	response = get(hh_url, params=payload)
	response.raise_for_status()
	return response.json()
	
	
def get_superjob_vacancies(superjob_token, 
			   page, 
			   language):
	superjob_url = "https://api.superjob.ru/2.0/vacancies/"
	programmist_key_id = 48
	payload = {
		"town": "Moscow",
		"keyword": f"Программист {language}",
		"key": programmist_key_id,
		"page": page,
	}
	headers = {"X-Api-App-Id": superjob_token}
	
				   headers=headers,)
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
	
	
def get_statistic_from_hh_vacancies(language,):
	rur_vacancies = 0
	salary_sum = 0
	max_page = 99
	
	for page in count(0):
		if page > max_page:
			break
			
		vacancies = get_hh_vacancies(language, page)
	
		for vacancy in vacancies["items"]:
			if not vacancy.get("salary"):
				continue
				
			salary = vacancy["salary"]
			approximate_salary = predict_rur_salary(salary["from"],
													salary["to"], 
													"RUR",
													salary["currency"],)
			if not predict_salary:
				continue
				
			rur_vacancies += 1
			salary_sum += approximate_salary
	
	if not rur_vacancies:
		average_salary = 0
	
	else:
		average_salary = salary_sum / rur_vacancies
	
	languages_statistic = {
		"vacancies_found": vacancies["found"],
		"vacancies_processed": rur_vacancies,
		"average_salary": average_salary,
	}
	return languages_statistic
	
	
def get_statistic_from_superjob_vacancies(language, superjob_token,):
	vacancies_found = 0
	vacancies_processed = 0
	salary_sum = 0
	max_page = 100
	
	for page in range(0, max_page+1):
		page_vacancies = get_superjob_vacancies(superjob_token, 
												page, 
												language,)
		
		for vacancy in page_vacancies:
			vacancies_found += 1
			salary = predict_rur_salary(
				vacancy["payment_from"], 
				vacancy["payment_to"], 
				"rub", 
				vacancy["currency"],
			)
			if not salary:
				continue
				
			vacancies_processed += 1
			salary_sum += salary
	
	if not rur_vacancies:
		average_salary = 0
	
	else:
		average_salary = salary_sum / vacancies_processed
		
	superjob_statistic = {
		"language": language,
		"vacancies_found": vacancies_found,
		"vacancies_processed": vacancies_processed,
		"average_salary": average_salary,
	}
	
	return superjob_statistic
	
	
def print_table(languages_statistic, title,):
	table_data = (
		["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата",],
	)	
	
	for language_statistic in languages_statistic:
		table_data += (languange_statistic["vacancies_found"],
					   languange_statistic["vacancies_processed"],
					   languange_statistic["average_salary"],)
		
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
		languages_hh_vacancies[language] = get_statistic_from_hh_vacancies(language,)
	
	print_table(languages_hh_vacancies, "HeadHunter",)
	
	languages_superjob_vacancies = {}
	
	for language in languages:
		languages_superjob_vacancies[language] = 
	get_statistic_from_superjob_vacancies(language, superjob_token,)
	
	print_table(languages_superjob_vacancies, "SuperJob",)
	
	
if __name__ == "__main__":
	main()
