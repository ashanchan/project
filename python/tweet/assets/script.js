var API_URL = 'https://bgjredujuf.execute-api.ap-south-1.amazonaws.com/prod/entries';

//=================================================
function getTweetSentiment() {
    $('#sentiment-loader').removeClass('hidden');
    $('#sentiment-holder').addClass("hidden");
    $.ajax({
        type: 'GET',
        url: API_URL,
        success: function(data) {
            showTweet(data);
        }
    });
    event.preventDefault();
}

//=================================================

function showTweet(data) {
    $('#entries').html('');
    $('#results').html('');
    dCtr = data.length;
    pCtr = 0;
    sCtr = 0;

    var line = '<table class="w3-table-all w3-hoverable">';
    line += '<tr class="w3-blue">';
    line += '<th>Tweets</th>';
    line += '<th>Polarity</th>';
    line += '<th>Subjectivity</th>';
    line += '</tr>';
    data.forEach(function(tweet) {
        line += '<tr>';
        line += '<td>' + tweet['tweet'] + '</td>';
        line += '<td><span class="w3-small w3-teal w3-right">' + String(tweet['polarity']).substring(0, 5) + '</span></td>';
        line += '<td><span class="w3-small w3-blue w3-right">' + String(tweet['subjectivity']).substring(0, 5) + '</span></td>';
        line += '</tr>';
        pCtr += tweet['polarity'];
        sCtr += tweet['subjectivity'];
    });
    line += '</table>';

    $('#table').append(line);
    $('#results').append('<div class="w3-bar-item">Sampled Tweet : ' + dCtr + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Samples : ' + dCtr + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Polarity : ' + (pCtr / dCtr) + '</div>');
    $('#results').append('<div class="w3-bar-item">Total Subjectivity : ' + (sCtr / dCtr) + '</div>');

    $('#sentiment-loader').addClass("hidden");
    $('#sentiment-holder').removeClass("hidden");
}

//=================================================