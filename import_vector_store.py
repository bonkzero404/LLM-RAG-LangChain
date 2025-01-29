from pprint import pprint
from vector_document import VectorDocument
from vector_store_documents import VectorStoreDocuments

vector_document = VectorDocument()
new_doc = vector_document.chunk_documents_by_subtopic(vector_document.load_documents())
pprint(new_doc)

store = VectorStoreDocuments()
vs = store.vector_store()
vs.remove_collection()
vs.store_documents(new_doc)

out = vs.retriever().invoke(input="Siapa CEO JuraganKlod?", k=2)
print("====================================")
print("INVOKE RESULT")
pprint(out)