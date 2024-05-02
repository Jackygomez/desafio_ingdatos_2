import csv

data = """
''52,923454''|''-1,474217''
''53,457321''|''-2,262773''
''50,871446''|''-0,729985''
''50,215687''|''-5,191573''
''57,540178''|''-3,758607''
''nan''|''nan''
''52,248118''|''0,109363''
"""

csv_reader = csv.reader(data.strip().splitlines(), delimiter='|', quotechar="'")

for row in csv_reader:
    cleaned_row = []
    for value in row:
        # Remover las comillas dobles exteriores
        clean_value = value.strip("'")
        
        # Reemplazar comas por puntos y manejar correctamente los números negativos
        clean_value = clean_value.replace(",", ".")
        
        # Convertir a float o manejar 'nan' como 0.0
        try:
            float_value = float(clean_value)
        except ValueError:
            float_value = 0.0
        
        cleaned_row.append(float_value)
        
    print(cleaned_row)


