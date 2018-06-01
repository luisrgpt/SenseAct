using System;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Windows.ApplicationModel;
using Windows.System;
using Windows.UI.Core;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media.Imaging;

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
private BatchesItemViewModel hidden_batches
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

    var data = Encoding.UTF8.GetBytes("quit_input");
    try
    {
        stream.Write(data, 0, data.Length);
    }
    catch (Exception) {}
    socket_client.Close();
}

private async void OnThreadStartAsync() {
    var server = "127.0.0.1";
    var port = 3000;

    var size = 100000;
    var data = new byte[size];

    var encoding = Encoding.UTF8;

    var separator = new char[] { '\r', '\n' };
    var options = StringSplitOptions.RemoveEmptyEntries;

    var pattern = ",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))";
    var csv_regex = new Regex(pattern);

    var priority = CoreDispatcherPriority.Normal;

    socket_client = new TcpClient(server, port);
    stream = socket_client.GetStream();

    var ack = Encoding.UTF8.GetBytes("ack_input");
    stream.Write(ack, 0, ack.Length);

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
    catch (Exception) {}
}

private void UpdatePage(string[] csv)
{
    System.Diagnostics.Debug.Write(csv.Length + " -> ");
    System.Diagnostics.Debug.WriteLine(String.Join(",", csv));
    if (csv[0] == "previous") {
        PreviousDelegate = ApplyPrevious;
        Previous.IsEnabled = true;
        return;
    }
    if (csv[0] == "next") {
        NextDelegate = ApplyNext;
        Next.IsEnabled = true;
        return;
    }
    if (csv[0] == "pause") {
        var symbol_icon = Pause.Content as SymbolIcon;
        symbol_icon.Symbol = Symbol.Pause;
        PauseDelegate = ApplyPause;
        Pause.IsEnabled = true;
        return;
    }
    if (csv[0] == "play") {
        var symbol_icon = Pause.Content as SymbolIcon;
        symbol_icon.Symbol = Symbol.Play;
        PauseDelegate = ApplyPlay;
        Pause.IsEnabled = true;
        return;
    }
    if (csv[0] == "stop") {
        StopDelegate = ApplyStop;
        Stop.IsEnabled = true;
        return;
    }
    if (csv[0] == "repeat-all") {
        RepeatAllDelegate = ApplyRepeatAll;
        RepeatAll.IsEnabled = true;
        return;
    }

    ship.ShipViewItems.Clear();
    submarine.SubmarineViewItems.Clear();
    batches.BatchesViewItems.Clear();
    if (csv[0] == "reset") {
        return;
    }
    var vals = csv.Skip(1);

    foreach (var val in vals.Take(4))
    {
        var item = new ShipViewItem()
        {
            Attribute = val
        };

        ship.ShipViewItems.Add(item);
    }
    vals = vals.Skip(4);

    foreach (var val in vals.Take(2))
    {
        var item = new SubmarineViewItem()
        {
            Attribute = val
        };

        submarine.SubmarineViewItems.Add(item);
    }
    vals = vals.Skip(2);

    Graph.Source = new BitmapImage
    {
        UriSource = new Uri(vals.First())
    };
    vals = vals.Skip(1);

    while (vals.Count() > 0)
    {
        var probe = new BatchesViewItem();
        batches.BatchesViewItems.Add(probe);

        foreach (var val in vals.Take(9))
        {
            var item = new BatchViewItem
            {
                Attribute = "      " + val + " "
            };
            probe.BatchViewItems.Add(item);
        }

        vals = vals.Skip(9);
    }

    var data = Encoding.UTF8.GetBytes("ack_input");
    stream.Write(data, 0, data.Length);
}

private void ApplyPrevious()
{

}

private void ApplyNext()
{
    Previous.IsEnabled = false;
    Next.IsEnabled = false;
    Pause.IsEnabled = false;
    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    PreviousDelegate = null;
    NextDelegate = null;
    PauseDelegate = null;
    StopDelegate = null;
    RepeatAllDelegate = null;

    var data = Encoding.UTF8.GetBytes("next_input");
    stream.Write(data, 0, data.Length);
}

private void ApplyPause()
{
    Previous.IsEnabled = false;
    Next.IsEnabled = false;
    Pause.IsEnabled = false;
    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    PreviousDelegate = null;
    NextDelegate = null;
    PauseDelegate = null;
    StopDelegate = null;
    RepeatAllDelegate = null;

    var data = Encoding.UTF8.GetBytes("pause_input");
    stream.Write(data, 0, data.Length);
}

private void ApplyPlay()
{
    Previous.IsEnabled = false;
    Next.IsEnabled = false;
    Pause.IsEnabled = false;
    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    PreviousDelegate = null;
    NextDelegate = null;
    PauseDelegate = null;
    StopDelegate = null;
    RepeatAllDelegate = null;

    var data = Encoding.UTF8.GetBytes("play_input");
    stream.Write(data, 0, data.Length);
}

private void ApplyStop()
{
    Previous.IsEnabled = false;
    Next.IsEnabled = false;
    Pause.IsEnabled = false;
    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    PreviousDelegate = null;
    NextDelegate = null;
    PauseDelegate = null;
    StopDelegate = null;
    RepeatAllDelegate = null;

    var data = Encoding.UTF8.GetBytes("stop_input");
    stream.Write(data, 0, data.Length);
}

private void ApplyRepeatAll()
{
    Previous.IsEnabled = false;
    Next.IsEnabled = false;
    Pause.IsEnabled = false;
    Stop.IsEnabled = false;
    RepeatAll.IsEnabled = false;

    PreviousDelegate = null;
    NextDelegate = null;
    PauseDelegate = null;
    StopDelegate = null;
    RepeatAllDelegate = null;

    var data = Encoding.UTF8.GetBytes("repeat_all_input");
    stream.Write(data, 0, data.Length);
}

private Action PreviousDelegate;
private Action NextDelegate;
private Action PauseDelegate;
private Action StopDelegate;
private Action RepeatAllDelegate;

private void OnPreviousClick(object sender, RoutedEventArgs e) => PreviousDelegate?.Invoke();
private void OnNextClick(object sender, RoutedEventArgs e) => NextDelegate?.Invoke();
private void OnPauseClick(object sender, RoutedEventArgs e) => PauseDelegate?.Invoke();
private void OnStopClick(object sender, RoutedEventArgs e) => StopDelegate?.Invoke();
private void OnRepeatAllClick(object sender, RoutedEventArgs e) => RepeatAllDelegate?.Invoke();

private void OnKeyUp(
    object sender,
    KeyRoutedEventArgs e)
{
    switch (e.Key)
    {
        //case VirtualKey.H:
        //    PreviousDelegate?.Invoke();
        //    break;
        case VirtualKey.L:
            NextDelegate?.Invoke();
            break;
        case VirtualKey.Space:
            PauseDelegate?.Invoke();
            break;
        case VirtualKey.Escape:
            StopDelegate?.Invoke();
            break;
        case VirtualKey.R:
            RepeatAllDelegate?.Invoke();
            break;
    }
}
}
}
