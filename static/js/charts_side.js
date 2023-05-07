google.charts.load('current', { 'packages': ['corechart'] });
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    fetch('/emotion-counts')
        .then(response => response.json())
        .then(counts => {
            var pie_data = google.visualization.arrayToDataTable([
                ['Emotion', 'Count', { role: 'style' }],
                ['Angry', counts.angry_count, '#636efa'],
                ['Disgust', counts.disgust_count, '#ef553b'],
                ['Fear', counts.fear_count, '#00cc96'],
                ['Happy', counts.happy_count, '#ab63fa'],
                ['Sad', counts.sad_count, '#ffa15a'],
                ['Surprise', counts.surprise_count, '#19d3f3'],
                ['Neutral', counts.neutral_count, '#ff6692']
            ]);

            var emotionData = [
                ['Angry', counts.angry_count, '#636efa'],
                ['Disgust', counts.disgust_count, '#ef553b'],
                ['Fear', counts.fear_count, '#00cc96'],
                ['Happy', counts.happy_count, '#ab63fa'],
                ['Sad', counts.sad_count, '#ffa15a'],
                ['Surprise', counts.surprise_count, '#19d3f3'],
                ['Neutral', counts.neutral_count, '#ff6692']
            ];

            emotionData.sort((a, b) => b[1] - a[1]);

            var column_data = new google.visualization.DataTable();

            column_data.addColumn('string', 'Emotion');
            column_data.addColumn('number', 'Count');
            column_data.addColumn({ type: 'string', role: 'style' });

            column_data.addRows(emotionData);

            var pie_chart_options = {
                backgroundColor: '#0e1117',
                colors: ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692'],
                fontSize: 15,
                fontName: 'monospace',
                is3D: true,
                legend: { position: 'right', textStyle: { color: '#ffffff', fontSize: 15, fontName: 'monospace' } },
                title: 'Emotion Counts Pie Chart',
                titleTextStyle: { color: '#ffffff', fontName: 'monospace', fontSize: 15, bold: true, italic: false },
            };

            var column_chart_options = {
                backgroundColor: '#0e1117',
                fontSize: 15,
                fontName: 'monospace',
                hAxis: { title: 'Emotion', textStyle: { color: '#ffffff', fontSize: 15, fontName: 'monospace' }, titleTextStyle: { color: '#ffffff', fontName: 'monospace', fontSize: 15, bold: true, italic: false } },
                legend: { position: 'none' },
                titleTextStyle: { color: '#ffffff', fontName: 'monospace', fontSize: 15, bold: true, italic: false },
                title: 'Emotion Counts Column Chart',
                titleTextStyle: { color: '#ffffff', fontName: 'monospace', fontSize: 15, bold: true, italic: false },
                vAxis: { title: 'Count', textStyle: { color: '#ffffff', fontSize: 15, fontName: 'monospace' }, titleTextStyle: { color: '#ffffff', fontName: 'monospace', fontSize: 15, bold: true, italic: false } }
            };

            var pie_chart = new google.visualization.PieChart(document.getElementById('pie-chart'));
            var column_chart = new google.visualization.ColumnChart(document.getElementById("column-chart"));

            pie_chart.draw(pie_data, pie_chart_options);
            column_chart.draw(column_data, column_chart_options);
        });
}

function updateChart() {
    setInterval(drawChart, 500);
}

google.charts.setOnLoadCallback(updateChart);