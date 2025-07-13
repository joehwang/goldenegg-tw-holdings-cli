import shioaji as sj
import os
api = sj.Shioaji(simulation=True)
#api = sj.Shioaji()
accounts =  api.login(os.getenv("SHINO_API_KEY"), os.getenv("SHINO_SECRET"))
api.list_accounts()

#api.activate_ca(ca_path="/app/Sinopac.pfx",ca_passwd="F124909524",person_id="F124909524")
