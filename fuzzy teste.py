from fuzzywuzzy import fuzz


def fuzzy_analysis(heard_nickname, online_nicknames):
    matches = [(nome, fuzz.ratio(heard_nickname, nome)) for nome in online_nicknames]
    matches_filtrados = [match for match in matches if match[1] >= 65]
    return matches_filtrados

print(fuzzy_analysis('Gicola', ['Numca', 'Gica', 'Rafa', 'Nori', 'João Victor', 'Manoela', 'Gicas'])[0][0])