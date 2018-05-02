using System;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Windows.ApplicationModel;
using Windows.UI.Core;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;

// The Blank Page item template is documented at
// https://go.microsoft.com/fwlink/?LinkId=402352&clcid=0x409

namespace user_interface_1_wpf
{
/// <summary>
/// An empty page that can be used on its own or navigated
/// to within a Frame.
/// </summary>
public sealed partial class MainPage : Page
{
private const string path_name = "./";

private TcpClient socket_client;
private NetworkStream stream;
private ShipItemViewModel ship
    = new ShipItemViewModel();
private SubmarineItemViewModel submarine
    = new SubmarineItemViewModel();
private BatchesItemViewModel batches
    = new BatchesItemViewModel();

public MainPage()
{
    InitializeComponent();

    var thread = new Thread(OnThreadStartAsync);
    thread.Start();
}

private void OnSuspending(
    object sender,
    SuspendingEventArgs e)
{
    //Debug.WriteLine("quit");

    var data = Encoding.UTF8.GetBytes("quit");
    stream.Write(data, 0, data.Length);
    socket_client.Close();
}

private async void OnThreadStartAsync() {
    var server = Dns.GetHostName();
    var port = 3000;

    var size = 10000;
    var data = new byte[size];

    var encoding = Encoding.UTF8;

    var separator = new char[] { '\r', '\n' };
    var options = StringSplitOptions.RemoveEmptyEntries;

    var pattern = ",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))";
    var csv_regex = new Regex(pattern);

    var priority = CoreDispatcherPriority.Normal;

    socket_client = new TcpClient(server, port);
    stream = socket_client.GetStream();

    Application.Current.Suspending += OnSuspending;

    try
    {
        while (true)
        {
            var count = stream.Read(
                buffer: data,
                offset: 0,
                size: size
            );
            var responses = encoding.GetString(
                bytes: data,
                index: 0,
                count: count
            ).Split(
                separator: separator,
                options: options
            );

            foreach (var response in responses)
            {
                var csv = csv_regex.Split(response);
                void agile_callback()
                    => UpdatePage(csv);
                await Dispatcher.RunAsync(
                    priority: priority,
                    agileCallback: agile_callback
                );
            }
        }
    }
    catch (Exception) {
        Environment.Exit(0);
    }
}

private void UpdatePage(string[] csv)
{
    if (csv[0] == "reset")
        ResetPage();
    else if (csv[1] == "ship")
        UpdateShip(csv);
    else if (csv[1] == "submarine")
        UpdateSubmarine(csv);
    else if (csv[1] == "batch")
        UpdateBatches(csv);
}

private void UpdateBatches(string[] csv)
{
    bool predicate(BatchesViewItem item)
        => item.BatchViewItems[0].Attribute == csv[2];
    var batch = batches.BatchesViewItems.FirstOrDefault(
        predicate: predicate
    );
    if (csv.Length == 3)
    {
        batches.BatchesViewItems.Remove(batch);
        return;
    }

    var index = 0;
    if (batch == null)
    {
        batch = new BatchesViewItem();
        batches.BatchesViewItems.Add(batch);
        for (; index < csv.Length - 2; index++)
        {
            var item = new BatchViewItem();
            batch.BatchViewItems.Add(item);
        }
    }

    index = 0;
    for (; index < csv.Length - 2; index++)
    {
        batch.BatchViewItems[index].Attribute
            = csv[index + 2];

        batch.BatchViewItems[index]
            = batch.BatchViewItems[index];
    }
    for (; index < batch.BatchViewItems.Count(); index++)
    {
        batch.BatchViewItems.RemoveAt(csv.Length - 2);
    }
}

private void UpdateSubmarine(string[] csv)
{
    if (submarine.SubmarineViewItems.Count == 1)
    {
        submarine.SubmarineViewItems[0].Attribute = csv[2];

        submarine.SubmarineViewItems[0]
            = submarine.SubmarineViewItems[0];
    }
    else
    {
        var location = new SubmarineViewItem()
        {
            Attribute = csv[2]
        };

        submarine.SubmarineViewItems.Add(location);
    }
}

private void UpdateShip(string[] csv)
{
    if (ship.ShipViewItems.Count == 3)
    {
        ship.ShipViewItems[0].Attribute = csv[2];
        ship.ShipViewItems[1].Attribute = csv[4];
        ship.ShipViewItems[2].Attribute = csv[3];

        ship.ShipViewItems[0] = ship.ShipViewItems[0];
        ship.ShipViewItems[1] = ship.ShipViewItems[1];
        ship.ShipViewItems[2] = ship.ShipViewItems[2];
    }
    else
    {
        var location = new ShipViewItem()
        {
            Attribute = csv[2]
        };
        var result = new ShipViewItem()
        {
            Attribute = csv[4]
        };
        var cost = new ShipViewItem()
        {
            Attribute = csv[3]
        };

        ship.ShipViewItems.Add(location);
        ship.ShipViewItems.Add(result);
        ship.ShipViewItems.Add(cost);
    }
}

private void ResetPage()
{
    ship.ShipViewItems.Clear();
    submarine.SubmarineViewItems.Clear();
    batches.BatchesViewItems.Clear();
}

private void OnPreviousClick(
    object sender,
    RoutedEventArgs e)
{

}

private void OnNextClick(
    object sender,
    RoutedEventArgs e)
{

}

private void OnPauseClick(
    object sender,
    RoutedEventArgs e)
{
    var button = sender as Button;
    button.IsEnabled = false;
    button.Click -= OnPauseClick;

    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    var data = Encoding.UTF8.GetBytes("pause");
    stream.Write(data, 0, data.Length);

    var symbol_icon = button.Content as SymbolIcon;
    symbol_icon.Symbol = Symbol.Play;

    Stop.IsEnabled = true;
    RepeatAll.IsEnabled = true;

    button.Click += OnPlayClick;
    button.IsEnabled = true;
}

private void OnPlayClick(
    object sender,
    RoutedEventArgs e)
{
    var button = sender as Button;
    button.IsEnabled = false;
    button.Click -= OnPlayClick;

    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    var data = Encoding.UTF8.GetBytes("play");
    stream.Write(data, 0, data.Length);

    var symbol_icon = button.Content as SymbolIcon;
    symbol_icon.Symbol = Symbol.Pause;

    Stop.IsEnabled = true;
    RepeatAll.IsEnabled = true;

    button.Click += OnPauseClick;
    button.IsEnabled = true;
}

private void OnStopClick(
    object sender,
    RoutedEventArgs e)
{
    var button = sender as Button;
    button.IsEnabled = false;

    Pause.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    var data = Encoding.UTF8.GetBytes("stop");
    stream.Write(data, 0, data.Length);

    ResetPage();

    var pause_symbol_icon = Pause.Content as SymbolIcon;
    if (pause_symbol_icon.Symbol == Symbol.Pause) {
        Pause.Click -= OnPauseClick;
        pause_symbol_icon.Symbol = Symbol.Play;
        Pause.Click += OnPlayClick;
    }

    Pause.IsEnabled = true;
    RepeatAll.IsEnabled = true;
}

private void OnRepeatAllClick(
    object sender,
    RoutedEventArgs e)
{
    var button = sender as Button;
    button.IsEnabled = false;

    Pause.IsEnabled = false;
    Stop.IsEnabled = false;

    var data = Encoding.UTF8.GetBytes("repeat_all");
    stream.Write(data, 0, data.Length);

    Pause.IsEnabled = true;
    Stop.IsEnabled = true;

    button.IsEnabled = true;
}
}
}
