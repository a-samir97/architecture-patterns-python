@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocations(add_stock):
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)

    add_stock([
        (later_batch, sku, 100, '2024-06-02'),
        (early_batch, sku, 100, '2024-06-01'),
        (other_batch, other_sku, 100, None),
    ])

    data = {"orderid": random_orderid(), 'sku': sku, 'qty': 5}

    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 201
    assert r.json()['batchref'] == early_batch


@pytest.mark.usefixtures('restart_api')
def test_allocations_are_persisited(add_stock):
    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)

    add_stock([
        (batch1, sku, 10, '2024-06-02'),
        (batch2, sku, 10, '2024-06-01'),
    ])

    line1 = {"orderid": order1, 'sku': sku, 'qty': 10}
    line2 = {"orderid": order2, 'sku': sku, 'qty': 10}

    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=line1)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch1

    r = requests.post(f'{url}/allocate', json=line2)
    assert r.status_code == 201
    assert r.json()['batchref'] == batch2


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_out_of_stock(add_stock):
    sku, small_batch, order = random_sku(), random_batchref(), random_orderid()

    add_Stock([(small_batch, sku, 10, '2024-06-02')])

    data = {"orderid": order, 'sku': sku, 'qty': 40}

    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400

    assert r.json()['message'] == f'Out of stock for sku {sku}'


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_invalid_sku():
    unknown_sku, order = random_sku(), random_orderid()

    data = {"orderid": order, 'sku': unknown_sku, 'qty': 10}

    url = config.get_api_url()

    r = requests.post(f'{url}/allocate', json=data)

    assert r.status_code == 400

    assert r.json()['message'] == f'Invalid sku {unknown_sku}'


@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, order = random_sku(), random_orderid()
    add_stock([(random_batchref(), sku, 30, None)])

    r = requests.post(
        f'{config.get_api_url()}/allocate',
        json={'orderid': order, 'sku': sku, 'qty': 10}
    )

    assert r.status_code == 201
    assert r.json()['batchref']


@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order = random_sku(), random_orderid()

    r = requests.post(
        f'{config.get_api_url()}/allocate',
        json={'orderid': order, 'sku': unknown_sku, 'qty': 10}
    )

    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'
