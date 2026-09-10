// اكواد المنحنى الخاص بالمبيعات
const canvas = document.getElementById("salesChart");
const ctx = canvas.getContext("2d");
const gradient = ctx.createLinearGradient(0, 0, 0, 300);
gradient.addColorStop(0, "rgba(108, 45, 255, 0.30)");
gradient.addColorStop(0.7, "rgba(108, 45, 255, 0.08)");
gradient.addColorStop(1, "rgba(108, 45, 255, 0)");

const salesChart = new Chart(ctx, {

    type: "line",

    data: {
        labels: [
            "18 مايو",
            "19 مايو",
            "20 مايو",
            "21 مايو",
            "22 مايو",
            "23 مايو",
            "24 مايو"
        ],

        datasets: [{
            data: [
                1200,
                5200,
                4400,
                9600,
                5700,
                4600,
                7600
            ],

            borderColor: "#713cff",

            backgroundColor: gradient,

            fill: true,

            borderWidth: 2,

            tension: 0.45,

            pointRadius: 3,

            pointHoverRadius: 5,

            pointBackgroundColor: "#713cff",

            pointBorderColor: "#713cff",

            pointBorderWidth: 0
        }]
    },

    options: {

        responsive: true,

        maintainAspectRatio: false,

        interaction: {
            intersect: false,
            mode: "index"
        },

        plugins: {

            legend: {
                display: false
            },

            tooltip: {
                enabled: true,

                backgroundColor: "#171b24",

                titleColor: "#ffffff",

                bodyColor: "#ffffff",

                borderColor: "#2b3040",

                borderWidth: 1,

                padding: 10,

                displayColors: false,

                callbacks: {
                    label: function(context) {
                        return context.parsed.y.toLocaleString() + " د.ل";
                    }
                }
            }
        },

        scales: {

            x: {

                grid: {
                    display: false
                },

                border: {
                    display: false
                },

                ticks: {
                    color: "#9a9eaa",

                    font: {
                        size: 10
                    },

                    maxRotation: 0
                }
            },

            y: {

                beginAtZero: true,

                suggestedMax: 10000,

                ticks: {

                    color: "#9a9eaa",

                    font: {
                        size: 10
                    },

                    stepSize: 2000,

                    callback: function(value) {

                        if (value === 0) {
                            return "0";
                        }

                        return (value / 1000) + "K";
                    }
                },

                grid: {

                    color: "rgba(255,255,255,0.06)",

                    lineWidth: 1,

                    drawTicks: false
                },

                border: {
                    display: false
                }
            }
        }
    }
});