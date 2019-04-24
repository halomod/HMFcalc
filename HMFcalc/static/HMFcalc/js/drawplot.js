//The following creates the initial plot, which should be empty.
// I'll probably get some better defualt data in here
//initialdata = [[1,0.1],
//               [2,0.2],
//               [3,0.3],
//               [4,0.4]]

initialdata = [[null, null],
    [null, null],
    [null, null],
    [null, null]]

myplot = new Dygraph(document.getElementById("image-div"),
    initialdata,
    {
        legend: 'false',
        logscale: true
        //title: 'NYC vs. SF',
        //showRoller: true,
        //rollPeriod: 14,
        //customBars: true,
        //ylabel: 'Temperature (F)',
    });