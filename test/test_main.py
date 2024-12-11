import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configuração do WebDriver para todos os testes
@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    yield driver  # Disponibiliza o WebDriver para os testes
    driver.quit()  # Fecha o navegador após o teste

def test_page_title(driver):
    driver.get("http://localhost:8050")
    assert "Dash" in driver.title

def test_home(driver):
    driver.get("http://localhost:8050")
    time.sleep(2)
    title = driver.find_element(By.ID, "title")
    print(title)
    assert "Monitoramento de Consumo" == title.text

def test_add_graph(driver):
    driver.get("http://localhost:8050")
    time.sleep(2)
    button = driver.find_element(By.ID, "botao-add-produtos")
    button.click()
    time.sleep(1)

    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dropdown-produto"))
    )

    dropdown.click()

    option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Café']"))
    )
    option.click()

    assert "Café" in dropdown.text , f"Opção esperada: 'Café', atual: {dropdown.text}"
    
    button = driver.find_element(By.ID, "botao-criar")
    button.click()
    time.sleep(1)
    
    graph = driver.find_elements(By.ID, 'graphs-container')
    assert len(graph) > 0, "Gráfico em tempo real não encontrado na página"
    
    time.sleep(5)
    graph = driver.find_elements(By.ID, 'bar-graph')
    assert len(graph) > 0, "Gráfico de barras não encontrado na página"
    
    graph = driver.find_elements(By.ID, 'ranking')
    assert len(graph) > 0, "Ranking não encontrado na página"

def test_forecast(driver):
    driver.get("http://localhost:8050")
    time.sleep(2)
    button = driver.find_element(By.ID, "botao-previsao")
    button.click()
    time.sleep(1)
    
    title = driver.find_element(By.ID, "title")
    assert "Previsão" == title.text
    
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dropdown-produto-prever"))
    )

    dropdown.click()

    option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Café']"))
    )
    option.click()

    assert "Café" in dropdown.text , f"Opção esperada: 'Café', atual: {dropdown.text}"
    
    button = driver.find_element(By.ID, "botao-prever")
    button.click()
    time.sleep(5)
    
    graph = driver.find_elements(By.ID, 'graphs-container-previsao')
    assert len(graph) > 0, "Gráfico em tempo real não encontrado na página"

def test_config(driver):
    driver.get("http://localhost:8050")
    time.sleep(2)
    button = driver.find_element(By.ID, "botao-config")
    button.click()
    time.sleep(1)
    
    title = driver.find_element(By.ID, "title")
    assert "Configurações" == title.text
    
    input = driver.find_element(By.ID, "input-intervalo_padrao")
    input.clear()
    input.send_keys("50")
    
    button = driver.find_element(By.ID, "botao-salvar_config")
    button.click()
    time.sleep(1)
    
    button = driver.find_element(By.ID, "botao-previsao")
    button.click()
    time.sleep(1)
    
    previsao = driver.find_element(By.ID, "input-intervalo")
    assert "50" == previsao.get_attribute("value")
    