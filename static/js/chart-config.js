// Zamonaviy chart konfiguratsiyasi
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the stats page
    const statsChartsContainer = document.getElementById('stats-charts-container');
    if (!statsChartsContainer) return;
    
    // Set modern Chart.js defaults
    if (Chart) {
        Chart.defaults.font.family = "'Poppins', 'Roboto', 'Inter', sans-serif";
        Chart.defaults.color = '#757575';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Modern styling gradients
        const primaryGradient = (ctx) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(66, 133, 244, 0.7)');
            gradient.addColorStop(1, 'rgba(66, 133, 244, 0.1)');
            return gradient;
        };
        
        const successGradient = (ctx) => {
            const gradient = ctx.createLinearGradient(0, 0, 400, 0);
            gradient.addColorStop(0, 'rgba(29, 171, 72, 0.7)');
            gradient.addColorStop(1, 'rgba(29, 171, 72, 0.1)');
            return gradient;
        };
    }
    
    // Kunlik tashriflar grafigi
    const dailyVisitorsChart = document.getElementById('daily-visitors-chart');
    if (dailyVisitorsChart) {
        fetch('/api/stats/visitors?days=7')
            .then(response => response.json())
            .then(data => {
                const chartData = {
                    labels: data.labels,
                    datasets: [{
                        label: 'Kunlik tashriflar',
                        data: data.data,
                        fill: true,
                        backgroundColor: function(context) {
                            const ctx = context.chart.ctx;
                            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                            gradient.addColorStop(0, 'rgba(66, 133, 244, 0.4)');
                            gradient.addColorStop(1, 'rgba(66, 133, 244, 0.05)');
                            return gradient;
                        },
                        borderColor: 'rgba(66, 133, 244, 1)',
                        tension: 0.4,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: 'rgba(66, 133, 244, 1)',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: 'rgba(66, 133, 244, 1)',
                        pointHoverBorderColor: '#FFFFFF',
                        pointHoverBorderWidth: 2
                    }]
                };
                
                const chartOptions = {
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 16,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 14
                            },
                            padding: 15,
                            cornerRadius: 8,
                            caretSize: 6,
                            callbacks: {
                                label: function(context) {
                                    return `Tashriflar: ${context.raw}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                precision: 0,
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        }
                    },
                    elements: {
                        line: {
                            borderWidth: 3
                        }
                    },
                    layout: {
                        padding: 20
                    },
                    interaction: {
                        mode: 'index',
                        intersect: false
                    }
                };
                
                new Chart(dailyVisitorsChart, {
                    type: 'line',
                    data: chartData,
                    options: chartOptions
                });
            })
            .catch(error => {
                console.error('Error fetching visitor data:', error);
                dailyVisitorsChart.innerHTML = '<div class="alert alert-danger">Ma\'lumotlarni yuklashda xatolik yuz berdi</div>';
            });
    }
    
    // Soatli statistika grafigi
    const hourlyStatsChart = document.getElementById('hourly-stats-chart');
    if (hourlyStatsChart) {
        fetch('/api/stats/hourly')
            .then(response => response.json())
            .then(data => {
                const chartData = {
                    labels: data.labels,
                    datasets: [{
                        label: 'Soatlik tashriflar',
                        data: data.data,
                        backgroundColor: function(context) {
                            const ctx = context.chart.ctx;
                            const gradient = ctx.createLinearGradient(0, 0, 0, 250);
                            gradient.addColorStop(0, 'rgba(75, 192, 192, 0.7)');
                            gradient.addColorStop(1, 'rgba(75, 192, 192, 0.2)');
                            return gradient;
                        },
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        borderRadius: 8,
                        borderSkipped: false,
                        maxBarThickness: 25
                    }]
                };
                
                const chartOptions = {
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 16,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 14
                            },
                            padding: 15,
                            cornerRadius: 8,
                            caretSize: 6
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                precision: 0,
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        }
                    },
                    layout: {
                        padding: 15
                    }
                };
                
                new Chart(hourlyStatsChart, {
                    type: 'bar',
                    data: chartData,
                    options: chartOptions
                });
            })
            .catch(error => {
                console.error('Error fetching hourly data:', error);
                hourlyStatsChart.innerHTML = '<div class="alert alert-danger">Ma\'lumotlarni yuklashda xatolik yuz berdi</div>';
            });
    }
    
    // Eng ko'p ko'rilgan mahsulotlar grafigi
    const productViewsChart = document.getElementById('product-views-chart');
    if (productViewsChart) {
        fetch('/api/stats/products')
            .then(response => response.json())
            .then(data => {
                const chartData = {
                    labels: data.labels,
                    datasets: [{
                        label: 'Mahsulot ko\'rishlari',
                        data: data.data,
                        backgroundColor: function(context) {
                            const ctx = context.chart.ctx;
                            const gradient = ctx.createLinearGradient(0, 0, 400, 0);
                            gradient.addColorStop(0, 'rgba(255, 99, 132, 0.7)');
                            gradient.addColorStop(1, 'rgba(255, 99, 132, 0.2)');
                            return gradient;
                        },
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                };
                
                const chartOptions = {
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 16,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 14
                            },
                            padding: 15,
                            cornerRadius: 8,
                            caretSize: 6
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                precision: 0,
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        y: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                padding: 10,
                                font: {
                                    size: 12
                                }
                            }
                        }
                    },
                    layout: {
                        padding: 15
                    }
                };
                
                new Chart(productViewsChart, {
                    type: 'bar',
                    data: chartData,
                    options: chartOptions
                });
            })
            .catch(error => {
                console.error('Error fetching product view data:', error);
                productViewsChart.innerHTML = '<div class="alert alert-danger">Ma\'lumotlarni yuklashda xatolik yuz berdi</div>';
            });
    }
    
    // Ommabop kategoriyalar grafigi
    const categoryViewsChart = document.getElementById('category-views-chart');
    if (categoryViewsChart) {
        fetch('/api/stats/categories')
            .then(response => response.json())
            .then(data => {
                const chartData = {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(255, 159, 64, 0.8)',
                            'rgba(231, 233, 237, 0.8)',
                            'rgba(96, 125, 139, 0.8)'
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 3,
                        hoverOffset: 15
                    }]
                };
                
                const chartOptions = {
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 16,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 14
                            },
                            padding: 15,
                            cornerRadius: 8,
                            caretSize: 6,
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return ` ${label}: ${value} ko'rishlar (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '40%',
                    layout: {
                        padding: 15
                    }
                };
                
                new Chart(categoryViewsChart, {
                    type: 'doughnut',
                    data: chartData,
                    options: chartOptions
                });
            })
            .catch(error => {
                console.error('Error fetching category data:', error);
                categoryViewsChart.innerHTML = '<div class="alert alert-danger">Ma\'lumotlarni yuklashda xatolik yuz berdi</div>';
            });
    }
});
