using System.Collections.ObjectModel;
using Windows.UI.Xaml.Controls;

namespace user_interface_1_wpf
{
    class ShipItemViewModel
    {
        private ObservableCollection<ShipViewItem> ship_view_items = new ObservableCollection<ShipViewItem>();

        public ObservableCollection<ShipViewItem> ShipViewItems {
            get => ship_view_items;
            set => ship_view_items = value;
        }
    }
}
