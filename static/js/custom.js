var is_authenticated = false;

function showToasts(message, messageType) {
    const toastContainer = document.getElementById('toastContainer');
    let toast = document.getElementById('liveToast');
    if (toast) {
        toastContainer.removeChild(toast);
    }
    toast = document.createElement('div');
    toast.classList.add('toast', messageType == 'success' ? 'text-bg-success' : 'text-bg-danger');
    toast.setAttribute('id', 'liveToast');
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    const div = document.createElement('div');
    div.classList.add('d-flex');
    const toastBody = document.createElement('div');
    toastBody.classList.add('toast-body');
    const b = document.createElement('b');
    b.innerHTML = message;
    toastBody.appendChild(b);
    div.appendChild(toastBody);
    const button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.classList.add('btn-close', 'me-2', 'm-auto');
    button.setAttribute('data-bs-dismiss', 'toast');
    button.setAttribute('aria-label', 'Close');
    div.appendChild(button);
    toast.appendChild(div);
    toastContainer.appendChild(toast);
    const toastLiveExample = document.getElementById('liveToast')
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
    toastBootstrap.show()
}

function showLoadingDiv() {
    var bcgDiv = document.getElementById("divBackground");
    var divWaitForPageLoad = document.getElementById("divWaitForPageLoad");
    bcgDiv.style.display = "block";
    divWaitForPageLoad.style.display = "block";
    if (bcgDiv != null) {
        bcgDiv.style.height = "100vh";
        bcgDiv.style.width = "100%";
    }
}

function hideLoadingDiv() {
    var bcgDiv = document.getElementById("divBackground");
    var divWaitForPageLoad = document.getElementById("divWaitForPageLoad");
    bcgDiv.style.display = "none";
    divWaitForPageLoad.style.display = "none";
}

function checkUploadStatus(buoy_id) {
    setTimeout(() => {
        $.ajax({
            url: `/api/uploadStatus/${buoy_id}/`,
            type: 'GET',
            success: function (response) {
                if (response.messageType == 'success' && response.data && response.data.status === 'In Progress') {
                    progress = response.data.current / response.data.total * 100;
                    progress = Math.round(progress * 100) / 100
                    document.getElementById('loading-progress').innerHTML = `${progress} %`;
                    setTimeout(() => {
                        checkUploadStatus(buoy_id)
                    }, 500);
                }
            },
            error: function (error) {
                showToasts(error.responseJSON.message, error.responseJSON.messageType);
            }
        });
    }, 1000);
}

function uploadData(buoy_id) {
    const form = document.getElementById('uploadForm');
    if (!form.file.value) {
        showToasts('Debe seleccionar un archivo', 'error');
        return;
    }
    // lock screen with a loading message
    console.log('uploading data');
    showLoadingDiv();
    const formData = new FormData(form);
    $.ajax({
        url: `/api/insertData/${buoy_id}/`,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            showToasts(response.message, response.messageType);
        },
        error: function (error) {
            showToasts(error.responseJSON.message, error.responseJSON.messageType);
        },
        complete: function () {
            form.reset();
            console.log('finished uploading data');
            hideLoadingDiv();
            getBuoy(buoy_id);
        }
    });
    document.getElementById('loading-progress').innerHTML = '0 %';
    checkUploadStatus(buoy_id);
}

function plotWithEChart(data, parameter, container) {
    const eChart = echarts.init(container);
    charts.push({
        parameter_id: parameter.id,
        chart: eChart
    });
    data = data.map((item) => {
        return {
            name: item.timestamp,
            value: [
                item.timestamp,
                item.value
            ]
        }
    });
    option = {
        tooltip: {
            trigger: 'axis',
            position: function (pt) {
                return [pt[0], '10%'];
            }
        },
        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                restore: {},
                saveAsImage: {}
            }
        },
        grid: {
            top: '12%',
            containLabel: true
        },
        xAxis: {
            type: 'time',
            splitLine: {
                show: false
            }
        },
        yAxis: {
            name: `${parameter.fullname}(${parameter.uom})`,
            min: parameter.min,
            max: parameter.max,
            type: 'value',
            boundaryGap: [0, '100%'],
            splitLine: {
                show: false
            },
            axisLine: {
                show: true,
            },
            axisTick: {
                show: true,
            }
        },
        dataZoom: [{
            type: 'slider',
            show: true,
            handleSize: 8
        },
        {
            type: 'inside',
        },
        {
            type: 'slider',
            show: true,
            yAxisIndex: 0,
            filterMode: 'empty',
            width: 12,
            height: '70%',
            handleSize: 8,
            showDataShadow: false,
            left: '93%'
        }],
        series: [
            {
                type: 'line',
                smooth: true,
                data: data,
            }
        ]
    };

    eChart.setOption(option);
    window.addEventListener('resize', function () {
        charts.forEach((chart) => {
            chart.chart.resize();
        })
    });
}

function addParameterFilters(buoy_id, parameter) {
    const displayClass = is_authenticated ? 'd-block' : 'd-none';
    const container = document.querySelector('#charts-container');
    const formContainer = document.createElement('div');
    formContainer.classList.add('card', 'p-4', 'mb-2');
    formContainer.setAttribute('id', `container-${parameter.id}`);
    formContainer.setAttribute('style', 'width: 100%');
    formContainer.innerHTML = `
        <form id="filterForm-${parameter.id}" class="mb-3">
            <div class="row mb-2">
                <div class="col">
                    <h5 class="medium-blue roboto-medium">${parameter.fullname}</h5>
                </div>
            </div>
            <div id="${parameter.id}-datetime-inputs" class="${displayClass}">
                <div class="row mb-3">
                    <div class="col-md-2">
                        <label for="" class="form-label">Fecha y Hora Inicial</label>
                    </div>
                    <div class="col-md-5">
                        <input type="date" class="form-control" id="startdate-${parameter.id}" name="startdate"
                            value="null">
                    </div>
                    <div class="col-md-5">
                        <input type="time" class="form-control" id="starttime-${parameter.id}" name="starttime"
                            value="00:00">
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-2">
                        <label for="" class="form-label">Fecha y Hora Final</label>
                    </div>
                    <div class="col-md-5">
                        <input type="date" class="form-control" id="enddate-${parameter.id}" name="enddate"
                            value="null">
                    </div>
                    <div class="col-md-5">
                        <input type="time" class="form-control" id="endtime-${parameter.id}" name="endtime" 
                            value="00:00">
                    </div>
                </div>
            </div>
        </form>
        <div class="d-flex justify-content-between mb-5">
            <div class="d-flex">
                <div class="me-1">
                    <input type="radio" class="btn-check" name="options-outlined-${parameter.id}" id="chart-checkbox-${parameter.id}" autocomplete="off" checked>
                    <label class="btn btn-outline-primary" for="chart-checkbox-${parameter.id}">Gráfica</label>
                </div>
                <div class="me-1">
                    <input type="radio" class="btn-check" name="options-outlined-${parameter.id}" id="table-checkbox-${parameter.id}" autocomplete="off">
                    <label class="btn btn-outline-primary" for="table-checkbox-${parameter.id}">Tabla</label>
                </div>
            </div>
            <div class="d-flex">        
                <div id="search-data-div-${parameter.id}" class="${displayClass} me-1">
                    <button class="btn btn-primary" id="search-data-${parameter.id}" onclick="getDataByBuoyAndParameterId(${buoy_id}, ${parameter.id})">BUSCAR</button>
                </div>
                <div id="export-data-div-${parameter.id}" class="${displayClass}">
                    <button class="btn btn-primary" id="export-data-${parameter.id}">DESCARGAR CSV</button>
                </div>
            </div>
        </div>
    `;
    container.appendChild(formContainer);
    filterForm = document.getElementById(`filterForm-${parameter.id}`);
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
    });
    document.getElementById(`chart-checkbox-${parameter.id}`).addEventListener('click', () => {
        document.getElementById(`table-container-${parameter.id}`).setAttribute('style', 'width: 100%; display: none;');
        document.getElementById(`chart-container-${parameter.id}`).setAttribute('style', 'width: 100%; height: 500px; display: block;');
        charts.forEach((chart) => {
            chart.chart.resize();
        })
    });
    document.getElementById(`table-checkbox-${parameter.id}`).addEventListener('click', () => {
        document.getElementById(`chart-container-${parameter.id}`).setAttribute('style', 'width: 100%; height: 500px; display: none;');
        document.getElementById(`table-container-${parameter.id}`).setAttribute('style', 'width: 100%; display: block;');
    });
    document.getElementById(`export-data-${parameter.id}`).addEventListener('click', (e) => {
        console.log(e);
        getDataAsCSV(buoy_id, parameter);
    });
}

function addParameterTable(data, parameter) {
    const formContainer = document.querySelector(`#container-${parameter.id}`);
    const previousTable = document.getElementById(`table-container-${parameter.id}`);
    var display = 'none';
    if (previousTable) {
        display = previousTable.style.display;
        formContainer.removeChild(previousTable);
    }
    const tableContainer = document.createElement('div');
    tableContainer.setAttribute('id', `table-container-${parameter.id}`);
    tableContainer.setAttribute('style', `width: 100%; display: ${display};`);
    formContainer.appendChild(tableContainer);
    var table = document.createElement('table');
    table.setAttribute('id', `table-${parameter.id}`);
    table.classList.add('table', 'table-striped', 'table-hover');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Fecha y Hora Local</th>
                <th>Fecha y Hora GMT</th>
                <th>${parameter.name}</th>
            </tr>
        </thead>
        <tbody id="table-body-${parameter.id}">
        </tbody>
    `;
    tableContainer.appendChild(table);
    const tableBody = document.getElementById(`table-body-${parameter.id}`);
    data.forEach((item) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(item.timestamp).toLocaleString('es-ES')}</td>
            <td>${new Date(item.timestamp).toUTCString()}</td>
            <td>${item.errors ? item.errors : item.value}</td>
        `;
        tableBody.appendChild(tr);
    });
    $(`#table-${parameter.id}`).DataTable({
        destroy: true,
        ordering: false,
        searching: false,
        language: {
            url: '/static/js/es-ES.json',
        },
    });
}

function addParameterChart(data, parameter) {
    const container = document.querySelector(`#container-${parameter.id}`);
    const previousChart = document.getElementById(`chart-container-${parameter.id}`);
    var display = 'block';
    if (previousChart) {
        display = previousChart.style.display;
        container.removeChild(previousChart);
    }
    const chartContainer = document.createElement('div');
    chartContainer.setAttribute('id', `chart-container-${parameter.id}`);
    chartContainer.setAttribute('style', `width: 100%; height: 500px; display: ${display}`);
    container.appendChild(chartContainer);
    plotWithEChart(data, parameter, chartContainer)
}

// get measures of central tendency from data (mean, mode, median, std)
function addMeasuresOfCentralTendency(data, parameter) {
    const container = document.querySelector(`#container-${parameter.id}`);
    const previousMeasures = document.getElementById(`measures-${parameter.id}`);
    if (previousMeasures) {
        container.removeChild(previousMeasures);
    }
    const measuresContainer = document.createElement('div');
    measuresContainer.setAttribute('id', `measures-${parameter.id}`);
    measuresContainer.classList.add('card', 'mb-2');
    measuresContainer.innerHTML = `    
    <table>
        <tr class="medium-blue background-light-blue">
            <td>
                <div class="ms-5">Media</div>
            </td>
            <td data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="${data.mean}">
                ${Math.round((data.mean + Number.EPSILON) * 1000) / 1000}
            </td>
            <td style="width: 125px"></td>
            <td>Valor Mínimo</td>
            <td>${data.min}</td>
        </tr>
        <tr class="medium-blue">
            <td>
                <div class="ms-5">Moda</div>
            </td>
            <td data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="${data.mode}">
                ${Math.round((data.mode + Number.EPSILON) * 1000) / 1000}
            </td>
            <td style="width: 125px"></td>
            <td>Valor Máximo</td>
            <td>${data.max}</td>
        </tr>
        <tr class="medium-blue background-light-blue">
            <td>
                <div class="ms-5">Mediana</div>
            </td>
            <td data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="${data.median}">
                ${Math.round((data.median + Number.EPSILON) * 1000) / 1000}
            </td>
            <td style="width: 125px"></td>
            <td>Rango</td>
            <td>${data.max - data.min}</td>
        </tr>
        <tr class="medium-blue">
            <td>
                <div class="ms-5">Desviación Estándar</div>
            </td>
            <td data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="${data.std}">
                ${Math.round((data.std + Number.EPSILON) * 1000) / 1000}
            </td>
        </tr>
    </table>
    `;
    container.appendChild(measuresContainer);

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}

function setSearchRange(min, max, parameter) {
    const startDateInput = document.getElementById(`startdate-${parameter.id}`);
    const endDateInput = document.getElementById(`enddate-${parameter.id}`);
    if (min && max) {
        min = new Date(min);
        max = new Date(max);
        startDateInput.min = min.toISOString().split('T')[0];
        startDateInput.max = max.toISOString().split('T')[0];
        endDateInput.min = min.toISOString().split('T')[0];
        endDateInput.max = max.toISOString().split('T')[0];
    }
}
function getDataByBuoyAndParameterId(buoy_id, parameter_id) {
    const parameter = parameters.find((item) => item.id == parameter_id);
    getData(buoy_id, parameter);
}

function getData(buoy_id, parameter) {
    const startDateInput = document.getElementById(`startdate-${parameter.id}`);
    const startDate = startDateInput ? startDateInput.value : '';

    const startTimeInput = document.getElementById(`starttime-${parameter.id}`);
    const startTime = startTimeInput ? startTimeInput.value : '';

    const endDateInput = document.getElementById(`enddate-${parameter.id}`);
    const endDate = endDateInput ? endDateInput.value : '';

    const endTimeInput = document.getElementById(`endtime-${parameter.id}`);
    const endTime = endTimeInput ? endTimeInput.value : '';

    $.ajax({
        url: `/api/data/${buoy_id}/${parameter.id}/?startdate=${startDate}&starttime=${startTime}&enddate=${endDate}&endtime=${endTime}`,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            addMeasuresOfCentralTendency(response.data, parameter);
            addParameterChart(response.data.data, parameter);
            addParameterTable(response.data.data, parameter);
            setSearchRange(response.data.min_date, response.data.max_date, parameter)
        },
        error: function (error) {
            console.log(error);
            showToasts(error.responseJSON.message, error.responseJSON.messageType);
        }
    });
}

function getDataAsCSV(buoy_id, parameter) {
    const startDateInput = document.getElementById(`startdate-${parameter.id}`);
    const startDate = startDateInput ? startDateInput.value : '';

    const startTimeInput = document.getElementById(`starttime-${parameter.id}`);
    const startTime = startTimeInput ? startTimeInput.value : '';

    const endDateInput = document.getElementById(`enddate-${parameter.id}`);
    const endDate = endDateInput ? endDateInput.value : '';

    const endTimeInput = document.getElementById(`endtime-${parameter.id}`);
    const endTime = endTimeInput ? endTimeInput.value : '';

    const url = `/api/data/csv/${buoy_id}/${parameter.id}/?startdate=${startDate}&starttime=${startTime}&enddate=${endDate}&endtime=${endTime}`
    const a = document.createElement('a');
    a.href = url;
    a.click();
    window.URL.revokeObjectURL(url);
}

function handleClickParameter(buoy_id, parameter_id) {
    // if checkbox unchecked, remove chart
    if (!document.querySelector(`#parameter-checkbox-${parameter_id}`).checked) {
        const container = document.querySelector('#charts-container');
        const div = document.querySelector(`#container-${parameter_id}`);
        if (div) {
            container.removeChild(div);
        }
    }
    // remove existing chart with parameter id
    else {
        const container = document.querySelector('#charts-container');
        const div = document.querySelector(`#container-${parameter_id}`);
        if (div) {
            container.removeChild(div);
        }

        // supress chart from charts list
        const chart = charts.find((item) => item.parameter_id == parameter_id);
        if (chart) {
            charts = charts.filter((item) => item.parameter_id != parameter_id);
        }

        const parameter = parameters.find((item) => item.id == parameter_id);
        addParameterFilters(buoy_id, parameter);
        getData(buoy_id, parameter);
    }
}

function addBuoyParameters() {
    const container = document.querySelector('#parameters-container');
    container.innerHTML = '';
    if (parameters && parameters.length > 0) {
        parameters.forEach((parameter) => {
            const div = document.createElement('div');
            div.classList.add('form-check');
            div.innerHTML = `
                <input class="form-check-input parameter-checkbox" type="checkbox"
                    id="parameter-checkbox-${parameter.id}" data-parameter-id="${parameter.id}">
                <label class="form-check-label" for="flexCheckDefault" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="${parameter.description}">
                    ${parameter.fullname}
                </label>
            `
            container.appendChild(div);
        });
    }

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}

function getParameters(buoy_id) {
    $.ajax({
        url: `/api/buoyParameters/${buoy_id}`,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            if (response.messageType == 'success') {
                parameters = response.data;
                let checked = false;

                if (parameters && parameters.length > 0) {
                    addBuoyParameters();
                    const parameterCheckBoxes = document.getElementsByClassName('parameter-checkbox');
                    for (let i = 0; i < parameterCheckBoxes.length; i++) {
                        if (parameterCheckBoxes[i].checked) {
                            checked = true;
                            handleClickParameter(buoy_id, parameterCheckBoxes[i].dataset['parameterId']);
                        }
                        parameterCheckBoxes[i].addEventListener('click', () => {
                            handleClickParameter(buoy_id, parameterCheckBoxes[i].dataset['parameterId']);
                        });
                    }

                    if (!checked) {
                        parameterCheckBoxes[0].checked = true;
                        handleClickParameter(buoy_id, parameterCheckBoxes[0].dataset['parameterId']);
                    }
                }
            }
        },
        error: function (error) {
            console.log(error);
            showToasts(error.responseJSON.message, error.responseJSON.messageType);
        }
    });
}

function getBuoy(buoy_id) {
    $.ajax({
        url: `/api/buoys/${buoy_id}/`,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            if (response.messageType == 'success') {
                buoy = response.data;
                getParameters(buoy.id);
            }
        },
        error: function (error) {
            console.log(error);
            showToasts(error.responseJSON.message, error.responseJSON.messageType);
        }
    });
}
