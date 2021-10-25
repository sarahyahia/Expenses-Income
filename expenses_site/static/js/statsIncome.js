const renderChart = (labels,data) => {

    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months Income',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title:{
                display : true,
                text: 'Income per Source'
            }
        }
    });
}

const getChartData=()=>{
    fetch('/income/income_source_summary')
    .then((res)=>res.json())
    .then((result)=>{
        const source_data = result.income_source_data;
        const [labels, data]=[
            Object.keys(source_data),
            Object.values(source_data),
        ]
        renderChart(labels,data)
    })
}

document.onload = getChartData();