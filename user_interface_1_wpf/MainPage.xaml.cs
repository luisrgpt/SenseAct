using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Windows.UI;
using Windows.UI.Core;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Media;

// The Blank Page item template is documented at https://go.microsoft.com/fwlink/?LinkId=402352&clcid=0x409

namespace user_interface_1_wpf
{
    /// <summary>
    /// An empty page that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainPage : Page
    {
        private const string path_name = "./";

        public MainPage()
        {
            this.InitializeComponent();

            Debug.WriteLine(String.Join("",
            Directory
                .EnumerateFiles(Path.GetFullPath(path_name), "*_current.csv", SearchOption.TopDirectoryOnly)
                .Select(file_name => {
                    OnChangedFileSystemEvent(this, new FileSystemEventArgs(
                        WatcherChangeTypes.Changed,
                        Path.GetDirectoryName(file_name),
                        Path.GetFileName(file_name)));
                    return "";
                })//; //strange but irrelevant bug
            ));

            FileSystemWatcher watcher = new FileSystemWatcher()
            {
                Path = path_name,
                Filter = "*_current.csv",
                EnableRaisingEvents = true
            };
            //watcher.Created += new FileSystemEventHandler(FileSystemEvent);
            watcher.Changed += new FileSystemEventHandler(OnChangedFileSystemEvent);
            watcher.Deleted += new FileSystemEventHandler(OnDeletedFileSystemEvent);
        }

        private void OnChangedFileSystemEvent(object source, FileSystemEventArgs args)
        {
            //Debug.WriteLine(args.FullPath);
            while(true)
            {
                try
                {
                    using (StreamReader reader = new StreamReader(args.FullPath))
                    {
                        String line = reader.ReadLine();

                        if (line.Equals(""))
                        {
                            return;
                        }

                        String[] parameters = new Regex(",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))").Split(line);
                        Task.Factory.StartNew(() => Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => UpdatePage(parameters)));
                    }

                    break;
                }
                catch (Exception)
                {
                    Thread.Sleep(100);
                }
            }
        }

        private void OnDeletedFileSystemEvent(object source, FileSystemEventArgs args)
        {
            //Debug.WriteLine(args.FullPath);
            Task.Factory.StartNew(() => Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => DeletePage(args.FullPath)));

        }

        private void DeletePage(string file_name) {
            foreach (Border border in this.Root.Children)
                this.Root.Children.Remove(border);
        }

        private String ship_text(String[] parameters)
            => parameters[01]
            + "\nLocal: " + parameters[02].Replace("\"", "")
            + "\nBalan: " + parameters[03].Replace("\"", "")
            + "\nValue: " + parameters[04].Replace("\"", "")
            + (parameters.Count() > 05 ? "\nAlerts:\n - " + String.Join("\n - ", parameters.Skip(05)) : "")
            ;
        private String submarine_text(String[] parameters)
            => parameters[01]
            + "\nLocal: " + parameters[02].Replace("\"", "")
            ;
        private String probe_text (String[] parameters) => parameters[03].Replace("\"", "");
        private Thickness probe_thickness (String[] parameters)
            => new Thickness
                ( 250 + 112 * (Int32.Parse(parameters[02]) % 7)
                , 040 + 41 * (Int32.Parse(parameters[02]) / 7)
                , 00
                , 00
                );

        private Thickness submarine_thickness = new Thickness(00, 40, 40, 40);
        private Thickness ship_thickness      = new Thickness(40, 40, 00, 40);
        private Thickness text_thickness      = new Thickness(10, 10, 10, 10);

        private SolidColorBrush ship_brush                = new SolidColorBrush(new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 }); //Blue
        private SolidColorBrush submarine_brush           = new SolidColorBrush(new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 }); //Red
        private SolidColorBrush probe_brush               = new SolidColorBrush(new Color() { A = 0xFF, R = 0x62, G = 0x75, B = 0x88 }); //Blue Grey
        private SolidColorBrush active_probe_brush        = new SolidColorBrush(new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 }); //Blue
        private SolidColorBrush hacked_probe_brush        = new SolidColorBrush(new Color() { A = 0xFF, R = 0x90, G = 0x6B, B = 0x6E }); //Red Grey
        private SolidColorBrush active_hacked_probe_brush = new SolidColorBrush(new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 }); //Red
        private SolidColorBrush text_brush                = new SolidColorBrush(Colors.White);

        private void UpdatePage(string[] parameters)
        {
            Border border = (Border)this.FindName(parameters[01] + parameters[02]);
            if (border == null)
            {
                this.Root.Children.Add(new Border()
                    { VerticalAlignment
                        = parameters[01] == "probe" ? VerticalAlignment.Top
                        : VerticalAlignment.Stretch
                    , HorizontalAlignment
                        = parameters[01] == "submarine" ? HorizontalAlignment.Right
                        : HorizontalAlignment.Left
                    , Background
                        = parameters[01] == "ship"                            ? ship_brush
                        : parameters[01] == "submarine"                       ? submarine_brush
                        : parameters.Length == 5 && parameters[04] == "False" ? probe_brush
                        : parameters.Length == 5                              ? active_probe_brush
                        : parameters[04] == "False"                           ? hacked_probe_brush
                        : active_hacked_probe_brush
                    , Margin
                        = parameters[01] == "ship"      ? ship_thickness
                        : parameters[01] == "submarine" ? submarine_thickness
                        : probe_thickness(parameters)
                    , Width
                        = parameters[01] == "ship"      ? 200
                        : parameters[01] == "submarine" ? 200
                        : 110
                    , Child = new TextBlock()
                        { Margin = text_thickness
                        , Text
                            = parameters[01] == "ship"      ? ship_text(parameters)
                            : parameters[01] == "submarine" ? submarine_text(parameters)
                            : probe_text(parameters)
                        , TextWrapping            = TextWrapping.Wrap
                        , FocusVisualPrimaryBrush = text_brush
                        , FontFamily              = new FontFamily("Consolas")
                        , FontSize                = 16
                        }
                    }
                );
            }
            else
            {
                ((TextBlock)border.Child).Text
                    = parameters[01] == "ship"      ? ship_text(parameters)
                    : parameters[01] == "submarine" ? submarine_text(parameters)
                    : probe_text(parameters);
            }
        }
    }
}
