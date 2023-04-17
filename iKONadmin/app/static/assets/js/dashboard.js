'use strict';
$(document).ready(function() {
    setTimeout(function() {
        // bar chart for Number of Players
        function age_player() {
            const chartDom = document.getElementById('age_player_bar');
            let age_player_bar = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'line'
                    }
                },
                legend: {
                    show: true
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: 'category',
                        data: ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60'],
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        axisLabel: {
                            formatter: '{value}%'
                        }
                    }
                ],
                series: [
                    {
                        name: 'Number of Players',
                        type: 'bar',
                        barWidth: '70%',
                        data: myData.age_player_bar,
                        itemStyle: {
                            color: '#899FD4'
                        },
                    }
                ]
            };
            option && age_player_bar.setOption(option);
        }
        age_player();

        // pie chart for Gender of Players
        function gender_player() {
            const chartDom = document.getElementById('gender_player_pie');
            let gender_player_pie = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'item'
                },
                series: [
                    {
                        name: 'Number of Players',
                        type: 'pie',
                        radius: '80%',
                        data: [
                            {value: myData.gender_player_pie[0], name: 'Female'},
                            {value: myData.gender_player_pie[1], name: 'Male'},
                            {value: myData.gender_player_pie[2], name: 'No response'}
                        ],
                        // itemStyle: {
                        //     color: '#899FD4'
                        // },
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            option && gender_player_pie.setOption(option);
        }
        gender_player();

        // bar chart for Income of Players
        function income_player() {
            const chartDom = document.getElementById('income_player_bar');
            let income_player_bar = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'line'
                    }
                },
                legend: {
                    show: true
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: 'category',
                        data: ['0-350', '350-800', '800-1400', '1400-2800', '2800-3500', '3500-5600', '>5600', 'No response'],
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        axisLabel: {
                            formatter: '{value}%'
                        }
                    }
                ],
                series: [
                    {
                        name: 'Number of Players',
                        type: 'bar',
                        barWidth: '70%',
                        data: myData.income_player_bar,
                        itemStyle: {
                            color: '#799FC8'
                        },
                    }
                ]
            };
            option && income_player_bar.setOption(option);
        }
        income_player();

        // pie chart for Location of Players
        function location_player() {
            const chartDom = document.getElementById('location_player_pie');
            let location_player_pie = echarts.init(chartDom);
            let option;

            let location_player_pie_arr = myData.location_player_pie
            let location_player_pie_cnt_arr = myData.location_player_pie_cnt
            let loc_data = []
            for (let i = 0; i < location_player_pie_arr.length; i++) {
                loc_data.push({value: location_player_pie_cnt_arr[i], name: location_player_pie_arr[i]})
            }

            option = {
                tooltip: {
                    trigger: 'item'
                },
                series: [
                    {
                        name: 'Number of Players',
                        type: 'pie',
                        radius: '80%',
                        data: loc_data,
                        // itemStyle: {
                        //     color: '#899FD4'
                        // },
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            option && location_player_pie.setOption(option);
        }
        location_player();

        // bar chart for Top Players by Number of Responses
        function top_response() {
            const chartDom = document.getElementById('top_response_bar');
            let top_response_bar = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                legend: {
                    show: true
                },
                xAxis: [
                    {
                        type: 'value'
                    }
                ],
                yAxis: [
                    {
                        type: 'category',
                        data: myData.top_response_bar_user,
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                series: [
                    {
                        name: 'Number of Responses',
                        type: 'bar',
                        barWidth: '80%',
                        data: myData.top_response_bar,
                        itemStyle: {
                            color: 'rgb(92, 107, 192)'
                        },
                    }
                ]
            };
            option && top_response_bar.setOption(option);
        }
        top_response();

        // bar chart for Top Players by Score
        function score_player() {
            const chartDom = document.getElementById('score_player_bar');
            let score_player_bar = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                legend: {
                    show: true
                },
                xAxis: [
                    {
                        type: 'value'
                    }
                ],
                yAxis: [
                    {
                        type: 'category',
                        data: myData.score_player_bar_user,
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                series: [
                    {
                        name: 'Score',
                        type: 'bar',
                        barWidth: '80%',
                        data: myData.score_player_bar,
                        itemStyle: {
                            color: '#5F9EA0'
                        },
                    }
                ]
            };
            option && score_player_bar.setOption(option);
        }
        score_player();

        // heatmap for Year Comparison
        function year_comparison() {
            const chartDom = document.getElementById('comparison_heat_map');
            let comparison_heat_map = echarts.init(chartDom);
            let option;

            const years = myData.year_comparison_years;
            let comparisons = myData.year_comparison_comparisons;
            let comparison_data = [];
            for (let i = 0; i < years.length; i++) {
                for (let j = 0; j < years.length; j++) {
                    comparison_data.push([i, j, comparisons[i*years.length+j] || '-'])
                }
            }

            option = {
                tooltip: {
                    axisPointer: {
                        type: 'cross',
                        crossStyle: { width: 0.1 }
                    },
                    showContent: false
                },
                grid: {
                    height: '85%',
                    top: '0%'
                },
                xAxis: {
                    type: 'category',
                    data: years,
                    splitArea: {
                        show: true
                    }
                },
                yAxis: {
                    type: 'category',
                    data: years,
                    splitArea: {
                        show: true
                    }
                },
                visualMap: {
                    min: 0,
                    max: Math.max(...comparisons),
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    inRange: {
                        color: '#313695',
                        colorLightness: [0.2, 1]
                    },
                    bottom: '0%'
                },
                series: [{
                    type: 'heatmap',
                    data: comparison_data,
                    label: {
                        show: true
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            option && comparison_heat_map.setOption(option);
        }
        year_comparison();

        // bar chart for Top Players by Frequency Referrals
        function referred_player() {
            const chartDom = document.getElementById('referral_player_bar');
            let referral_player_bar = echarts.init(chartDom);
            let option;

            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                legend: {
                    show: true
                },
                xAxis: [
                    {
                        type: 'value'
                    }
                ],
                yAxis: [
                    {
                        type: 'category',
                        data: myData.referral_player_bar_user,
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                series: [
                    {
                        name: 'Number of Referees',
                        type: 'bar',
                        barWidth: '80%',
                        data: myData.referral_player_bar,
                        itemStyle: {
                            color: '#99a9f5'
                        },
                    }
                ]
            };
            option && referral_player_bar.setOption(option);
        }
        referred_player();

    }, 1000);
});
