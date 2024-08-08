document.addEventListener('DOMContentLoaded', function() {
    // Mock data for TVL Chart
    var ctx = document.getElementById('tvlChart').getContext('2d');
    var tvlChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan-Mar', 'Apr-Jun', 'Jul-Sep', 'Oct-Dec'],
            datasets: [{
                label: '2021',
                data: [30, 32, 31, 35],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }, {
                label: '2022',
                data: [35, 37, 38, 43],
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Mock data for Protocols Chart
    var ctx2 = document.getElementById('protocolsChart').getContext('2d');
    var protocolsChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Ethereum', 'BSC', 'TRON'],
            datasets: [{
                data: [45, 30, 20],
                backgroundColor: ['#36a2eb', '#ffce56', '#ff6384']
            }]
        },
        options: {
            responsive: true
        }
    });
});
