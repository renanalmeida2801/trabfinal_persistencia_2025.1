import pandas as pd

path_participantes = 'PARTICIPANTES_2024.csv'
path_resultados = 'RESULTADOS_2024.csv'

N = 5000

print("carregando participantes...")
df_participantes = pd.read_csv(path_participantes, sep=';', encoding='latin1', nrows=N)
print("carregando resultados...")
df_resultados = pd.read_csv(path_resultados, sep=';', encoding='latin1', nrows=N)

print("\nColunas dos participantes:")
print(df_participantes.columns.tolist())

print("\nColunas dos resultados:")
print(df_resultados.columns.tolist())

df_participantes.to_csv('amostra_participantes.csv', index=False)
df_resultados.to_csv('amostra_resultados.csv', index=False)

print("\nAmostras salvas com sucesso!")