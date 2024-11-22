from fastapi import APIRouter, FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.app.modulos import livesports360_service, skysports_service, soccerway_service, sportsmole_service, soccerway_service_v2
import logging
import pandas as pd
from src.app.modulos import utils 


router = APIRouter(
    prefix="/gestor",
    tags=["gestor"])


host, port, db, usr, pwd = utils.get_values_database_postgress()


def save_db(data, ligue: int, season:int):
    print('Inicia insert db')
    conn = utils.conexion_postgres(host,port,db,usr,pwd)
    cursor = conn.cursor()
    for row in data:
        query = "insert into collection_data.match_v1(id_ligue, date_match,home_team, away_team, corner_count, scoring_team, half, time_match, conceding_player, id_season) values (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query,(ligue, row['date'],row['home_team'], row['away_team'], row['corner_count'], row['scoring_team'], row['half'], row['time'], row['conceding_player'], season))
        conn.commit()
        print('Insertado correctamente')
    if conn:
        cursor.close()
        conn.close()  
    
def core_get_data(url: str, ligue: int, season:int):
    print('Inica core get data')
    response = {}
    try:
        data = []
        intentos = 0
        
        while not data and intentos < 5:
            intentos = intentos + 1
            print(f'url: {url}, intento N° {intentos}')  
            
            if 'livesports360' in url :
                print('****LIVESPORT360***')
                data = livesports360_service.scraping(url)
            elif 'skysports' in url:
                print('****SKYSPORTS***')
                data = skysports_service.scraping(url)
            elif 'sportsmole' in url:
                print('****SPORTSMOLE***')
                data = sportsmole_service.scraping(url)
            elif 'soccerway' in url:
                print('****SOCCERWAY***')
                data = soccerway_service.scraping(url) # soccerway_service.scraping(url)
            
        if data:
            save_db(data, ligue, season)
            response = 'ok'
        else:
            response = 'empty'
        
    except Exception as error:
        response = 'error'
        print(f'Ocurrió un error:{error}')
    return response

@router.post("/upload-txt/", response_class=JSONResponse)
async def procesar_txt(file: UploadFile = File(...), ligue: int = Form(...), season: int = Form(...)):
    if file.content_type != 'text/plain':
        return "Invalid file type. Only TXT files are accepted."
    
    content = await file.read()
    lines = content.decode('utf-8').splitlines()
    
    processed_lines_error = []
    
    for line in lines:
        response_process = core_get_data(line, ligue, season)
        if response_process != 'ok' :
            processed_lines_error.append(line)
    
    return processed_lines_error


@router.get("/generate-csv/{id_ligue}")
async def generate_csv(id_ligue:int, id_season:int = None, fecha_inicio: str= None, fecha_fin:str = None):
    try:
        data=[]
        season = 'TODOS'
        ligue = ''
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        fecha_filtro = ''
        if fecha_inicio and fecha_fin:
            fecha_filtro = f" and date_match between '{fecha_inicio}' and '{fecha_fin}'"
            
        season_filtro = ''
        if id_season:
            season_filtro = f'and id_season = {id_season}'
        select_query = f"select date_match, replace(LTRIM(home_team),' ','_') as home_team , replace(LTRIM(away_team),' ','_') as away_team , corner_count, replace(LTRIM(scoring_team),' ','_') as scoring_team ,half, time_match , replace(LTRIM(conceding_player),' ','_') from collection_data.match_v1  where id_ligue =  %s {season_filtro} {fecha_filtro} order by date_match, home_team, corner_count asc"
        cursor.execute(select_query,(id_ligue, ))
        if cursor.rowcount > 0:
            data = cursor.fetchall()
            
            if id_season:
                select_query = "select name_season  from collection_data.season s  where id_season  =  %s "
                cursor.execute(select_query,(id_season, ))
                season = cursor.fetchone()
                season = season[0]
            
            select_query = "select name_ligue  from collection_data.ligue l  where id_ligue  =  %s "
            cursor.execute(select_query,(id_ligue, ))
            ligue = cursor.fetchone()
            ligue = ligue[0]                

        df = pd.DataFrame(data)
        df.to_csv(f'matches_{ligue}_{season}.csv', sep=';', index=False, header=False)
    except BaseException as error:
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    
    return "ok"
    
    
    

@router.get("/generate-excel/{id_ligue}")
async def generate_excel(id_ligue:int, id_season:int = None,fecha_inicio: str= None, fecha_fin:str = None):
    try:
        data=[]
        season = 'TODOS'
        ligue = ''
        conn = utils.conexion_postgres(host,port,db,usr,pwd)
        cursor = conn.cursor()
        fecha_filtro = ''
        if fecha_inicio and fecha_fin:
            fecha_filtro = f" and date_match between '{fecha_inicio}' and '{fecha_fin}'"
            
        season_filtro = ''
        if id_season:
            season_filtro = f'and id_season = {id_season}'
        select_query = f"select date_match, replace(LTRIM(home_team),' ','_') as home_team , replace(LTRIM(away_team),' ','_') as away_team , corner_count, replace(LTRIM(scoring_team),' ','_') as scoring_team ,half, time_match , replace(LTRIM(conceding_player),' ','_') from collection_data.match_v1  where id_ligue =  %s {season_filtro} {fecha_filtro} order by date_match, home_team, corner_count asc"
        cursor.execute(select_query,(id_ligue, ))
        if cursor.rowcount > 0:
            data = cursor.fetchall()
            
            if id_season:
                select_query = "select name_season  from collection_data.season s  where id_season  =  %s "
                cursor.execute(select_query,(id_season, ))
                season = cursor.fetchone()
                season = season[0]
            
            select_query = "select name_ligue  from collection_data.ligue l  where id_ligue  =  %s "
            cursor.execute(select_query,(id_ligue, ))
            ligue = cursor.fetchone()
            ligue = ligue[0]                

        df = pd.DataFrame(data)
        header = ['Date', 'Home_Team', 'Away_Team', 'Corner_Count', 'Scoring_Team', 'Half', 'Time', 'Conceding_Player']
        df.to_excel(f'matches_{ligue}_{season}.xlsx', index=False, header=header)
    except BaseException as error:
        print(f'Ocurrió un error inesperado: {error}')
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('conexion terminada')
    
    return "ok"
    