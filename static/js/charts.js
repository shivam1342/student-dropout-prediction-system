/**
 * Chart.js helper functions
 */

/**
 * Creates a line chart.
 * @param {CanvasRenderingContext2D} ctx - The context of the canvas element.
 * @param {string[]} labels - The labels for the x-axis.
 * @param {number[]} data - The data points for the y-axis.
 * @param {string} label - The label for the dataset.
 */
function createLineChart(ctx, labels, data, label) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                fill: false,
                borderColor: 'rgb(78, 115, 223)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100 // Risk score is 0-100
                }
            }
        }
    });
}
