from datetime import datetime, timezone, timedelta


def gerar_data(qtd):
    datas = []
    for num in range(qtd):
        data = datetime.now(timezone.utc) + timedelta(days=num, minutes=num, seconds=num)
        datas.append(data.strftime("%d/%m/%Y,%H:%M:%S"))
    
    
    return datas


def transacoes_do_dia(datas: list):
        data_hoje = datetime.now(timezone.utc).date()
        transasoes_dia = [transacao for transacao in datas if datetime.strptime(transacao,"%d/%m/%Y,%H:%M:%S" ).date() == data_hoje ]
            
        return transasoes_dia

print(transacoes_do_dia(gerar_data(20)))

print(transacoes_do_dia.__name__)