from pymed import PubMed

"""In MEDLINE/PubMed, every journal article is indexed with about 10–15 subject headings, 
subheadings and supplementary concept records, with some of them designated as major and marked 
with an asterisk, indicating the article's major topics. When performing a MEDLINE search via PubMed, 
entry terms are automatically translated into (i.e. mapped to) the corresponding descriptors with a 
good degree of reliability; it is recommended to check the 'Details tab' in PubMed to see how a search 
formulation was translated. By default, a search for a descriptor will include all the descriptors in 
the hierarchy below the given one. PubMed does not apply automatic mapping of the term in the following 
circumstances: by writing the quoted phrase (e.g., "kidney allograft"), when truncated on the asterisk 
(e.g., kidney allograft *), and when looking with field labels (e.g., Cancer [ti]).

Campos-Asensio, C. (2018). "Cómo elaborar una estrategia de búsqueda bibliográfica". 
Enfermería Intensiva (in Spanish). 29 (4): 182–186. """

pubmed = PubMed(tool="MyTool", email="my@email.address")
results = pubmed.query("spanish[Language]" , max_results=500)
for res in results:
    print(res)