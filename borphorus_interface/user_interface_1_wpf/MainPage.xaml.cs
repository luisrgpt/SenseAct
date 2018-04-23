using System;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Sockets;
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
            InitializeComponent();

            Thread thread = new Thread(OnThreadStart);
            thread.Start();
        }

        private void OnThreadStart() {
            String server = Dns.GetHostName();
            Int32 port = 3000;
            TcpClient socket_client = new TcpClient(server, port);
            using (NetworkStream stream = socket_client.GetStream())
            {
                Byte[] data = new Byte[256];
                String responseData = String.Empty;

                while (true)
                {
                    Int32 bytes = stream.Read(data, 0, data.Length);
                    responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
                    String[] parameters = new Regex(",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))").Split(responseData);
                    Task.Factory.StartNew(() => Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => UpdatePage(parameters)));
                }
            }
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
        private String batch_text(String[] parameters) => String.Join("\n", parameters);

        private int ship_width      = 210;
        private int submarine_width = 200;
        private int batch_width     = 250;

        private Thickness batch_thickness (String[] parameters)
            => new Thickness
                ( 260 + (batch_width + 10) * ((Int32.Parse(parameters[02]) - 1) % 3)
                , 040 + (150 + 41) * ((Int32.Parse(parameters[02]) - 1) / 3)
                , 00
                , 00
                );

        private Thickness ship_thickness      = new Thickness(40, 40, 00, 40);
        private Thickness submarine_thickness = new Thickness(00, 40, 40, 40);
        private Thickness text_thickness      = new Thickness(10, 10, 10, 10);

        private SolidColorBrush ship_brush                = new SolidColorBrush(new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 }); //Blue
        private SolidColorBrush submarine_brush           = new SolidColorBrush(new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 }); //Red
        private SolidColorBrush batch_brush               = new SolidColorBrush(new Color() { A = 0xFF, R = 0x62, G = 0x75, B = 0x88 }); //Blue Grey
        private SolidColorBrush active_batch_brush        = new SolidColorBrush(new Color() { A = 0xFF, R = 0x00, G = 0x78, B = 0xD7 }); //Blue
        private SolidColorBrush hacked_batch_brush        = new SolidColorBrush(new Color() { A = 0xFF, R = 0x90, G = 0x6B, B = 0x6E }); //Red Grey
        private SolidColorBrush active_hacked_batch_brush = new SolidColorBrush(new Color() { A = 0xFF, R = 0xE7, G = 0x48, B = 0x56 }); //Red
        private SolidColorBrush text_brush                = new SolidColorBrush(Colors.White);
        private int timestamp = 0;
        private void UpdatePage(string[] parameters)
        {
            Debug.WriteLine(timestamp + ": " + String.Join(",", parameters));

            if (parameters.Length == 0)
            {
                foreach (Border border in Root.Children)
                    Root.Children.Remove(border);

                return;
            }

            Border new_border = (Border)FindName(parameters[01] + parameters[02]);
            if (new_border == null)
            {
                Root.Children.Add(new Border()
                    { VerticalAlignment
                        = parameters[01] == "batch" ? VerticalAlignment.Top
                        : VerticalAlignment.Stretch
                    , HorizontalAlignment
                        = parameters[01] == "submarine" ? HorizontalAlignment.Right
                        : HorizontalAlignment.Left
                    , Background
                        = parameters[01] == "ship"                            ? ship_brush
                        : parameters[01] == "submarine"                       ? submarine_brush
                        : /*parameters.Length == 5 && parameters[04] == "False" ?*/ batch_brush
                        //: parameters.Length == 5                              ? active_batch_brush
                        //: parameters[04] == "False"                           ? hacked_batch_brush
                        //: active_hacked_batch_brush
                    , Margin
                        = parameters[01] == "ship"      ? ship_thickness
                        : parameters[01] == "submarine" ? submarine_thickness
                        : batch_thickness(parameters)
                    , Width
                        = parameters[01] == "ship"      ? ship_width
                        : parameters[01] == "submarine" ? submarine_width
                        : batch_width
                    , Child = new TextBlock()
                        { Margin = text_thickness
                        , Text
                            = parameters[01] == "ship"      ? ship_text(parameters)
                            : parameters[01] == "submarine" ? submarine_text(parameters)
                            : batch_text(parameters)
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
                ((TextBlock)new_border.Child).Text
                    = parameters[01] == "ship"      ? ship_text(parameters)
                    : parameters[01] == "submarine" ? submarine_text(parameters)
                    : batch_text(parameters);
            }
        }
    }
}
