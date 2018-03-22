using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
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

            Debug.WriteLine(String.Join(",",
            Directory
                .EnumerateFiles(Path.GetFullPath(path_name), "*.csv", SearchOption.TopDirectoryOnly)
                .Select(file_name => {UpdatePage(file_name); return file_name; })//; //strange but irrelevant bug
            ));

            FileSystemWatcher watcher = new FileSystemWatcher()
            {
                Path = path_name,
                Filter = "*.csv",
                EnableRaisingEvents = true
            };
            //watcher.Created += new FileSystemEventHandler(FileSystemEvent);
            watcher.Changed += new FileSystemEventHandler(FileSystemEvent);
            watcher.Deleted += new FileSystemEventHandler(OnDeletedFileSystemEvent);
        }

        private void FileSystemEvent(object source, FileSystemEventArgs args)
        {
            Debug.WriteLine(args.FullPath);
            Thread.Sleep(100);
            Task.Factory.StartNew(() => Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => { lock (this) { UpdatePage(args.FullPath); } }));
        }

        private void OnDeletedFileSystemEvent(object source, FileSystemEventArgs args)
        {
            Debug.WriteLine(args.FullPath);
            Thread.Sleep(100);
            Task.Factory.StartNew(() => Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => { lock (this) { DeletePage(args.FullPath); } }));

        }

        private void DeletePage(string file_name) {
            Border border = (Border)this.FindName(file_name);
            if (border != null)
            {
                this.Root.Children.Remove(border);
            }
        }

        private void UpdatePage(string file_name)
        {
            using (StreamReader reader = new StreamReader(file_name))
            {
                String line = reader.ReadLine();

                if (line.Equals("")) {
                    File.Delete(file_name);
                    return;
                }

                String[] parameters = reader.ReadLine().Split(',');

                Border border = (Border)this.FindName(file_name);
                if (border == null)
                {
                    this.Root.Children.Add(new Border()
                    {
                        Background = new SolidColorBrush(
                            parameters[01] == "red" ?
                            new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 } : //red
                            new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 }), //blue
                        HorizontalAlignment =
                            parameters[02] == "right" ?
                            HorizontalAlignment.Right : //right
                            HorizontalAlignment.Left,   //left
                        Margin = new Thickness(
                            Int32.Parse(parameters[03]),
                            Int32.Parse(parameters[04]),
                            Int32.Parse(parameters[05]),
                            Int32.Parse(parameters[06])),
                        Width = Int32.Parse(parameters[07]),

                        Child = new TextBlock()
                        {
                            Margin = new Thickness(10, 10, 10, 10),
                            Text = String.Join("\n", parameters.Skip(08)),
                            TextWrapping = TextWrapping.Wrap,
                            FocusVisualPrimaryBrush = new SolidColorBrush(Colors.White),
                            FontFamily = new FontFamily("Consolas"),
                            FontSize = 20
                        }
                    });
                }
                else
                {
                    ((TextBlock) border.Child).Text = String.Join("\n", parameters.Skip(08));
                }
            }
        }
    }
}
