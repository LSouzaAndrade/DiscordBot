from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/disconnect_user/")
async def disconnect_user(request: Request):
    try:
        data = await request.json()
        print("Payload recebido:", data)
        
        return JSONResponse(content={
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Requisição processada com sucesso."
                },
                "shouldEndSession": True
            }
        })

    except Exception as e:
        print("Erro ao processar a requisição:", str(e))
        return JSONResponse(status_code=422, content={"message": "Erro ao processar a requisição"})
