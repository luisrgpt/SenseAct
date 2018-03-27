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
            Border border = (Border)this.FindName(file_name);
            if (border != null)
                this.Root.Children.Remove(border);
        }

        private String submarine_text(String[] parameters)
            => parameters[01] + ": " + parameters[02]
            + "\nLocal: " + parameters[04].Replace("\"", "")
            + "\nBalan: " + parameters[05].Replace("\"", "")
            + (parameters.Count() > 06 ? "\nProbes:\n - " + String.Join("\n - ", parameters.Skip(06)) : "");
        private String probe_text (String[] parameters)
            => parameters[01] + ": " + parameters[02]
            + "\nLocal: " + parameters[04].Replace("\"", "")
            + "\nCost:  " + parameters[05]
            + "\nUncer: " + parameters[06]
            + "\nValue: " + Math.Round(float.Parse(parameters[07]), 6);
        private Thickness probe_thickness (String[] parameters)
            => new Thickness
                ( 250 + 210 * (Int32.Parse(parameters[02]) / 4)
                , 040 + 124 * (Int32.Parse(parameters[02]) % 4)
                , 00
                , 00
                );

        private Thickness       red_thickness = new Thickness(00, 40, 40, 40);
        private Thickness       blu_thickness = new Thickness(40, 40, 00, 40);
        private Thickness       txt_thickness = new Thickness(10, 10, 10, 10);
        private SolidColorBrush red_brush     = new SolidColorBrush(new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 });
        private SolidColorBrush blu_brush     = new SolidColorBrush(new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 });
        private SolidColorBrush txt_brush     = new SolidColorBrush(Colors.White);

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
                        = parameters[02] == "red" ? HorizontalAlignment.Right
                        : HorizontalAlignment.Left
                    , Background
                        = parameters[03] == "red" ? red_brush
                        : blu_brush
                    , Margin
                        = parameters[01] == "probe" ? probe_thickness(parameters)
                        : parameters[03] == "red" ? red_thickness
                        : blu_thickness
                    , Width
                        = 200
                    , Child = new TextBlock()
                        { Margin                  = txt_thickness
                        , Text
                            = parameters[01] == "probe" ? probe_text(parameters)
                            : submarine_text(parameters)
                        , TextWrapping            = TextWrapping.Wrap
                        , FocusVisualPrimaryBrush = txt_brush
                        , FontFamily              = new FontFamily("Consolas")
                        , FontSize                = 16
                        }
                    }
                );
            }
            else
            {
                ((TextBlock)border.Child).Text
                    = parameters[01] == "probe" ? probe_text(parameters)
                    : submarine_text(parameters);
            }
        }
    }
}
