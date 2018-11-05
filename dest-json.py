import json

def create_dest_dict():
	code = input("Enter destination code: ")
	destination = input("Enter destination name: ")
	info = input("Enter destination info: ")
	facts = []
	cont = 'y'
	while(cont == 'y'):
		facts.append(input("Enter a fact: "))
		cont = input("Add more facts? (y/n) :")
	destfact_dict = {
	"code" : code,
	"dest" : destination,
	"info" : info,
	"facts" : facts
	}
	return(destfact_dict)

def create_json_file():
	destfact_list = []
	cont = 'y'
	while(cont == 'y'):
		destfact_list.append(create_dest_dict())
		cont = input("Add more cities? (y/n) :")
	destfact_json = json.dumps(destfact_list)
	with open("destfact.json","w") as file:
		file.write(destfact_json)

if __name__ == "__main__":
	create_json_file()