using System.Collections.ObjectModel;

namespace user_interface_1_wpf
{
    class SubmarineItemViewModel
    {
        private ObservableCollection<SubmarineViewItem> submarine_view_items = new ObservableCollection<SubmarineViewItem>();

        public ObservableCollection<SubmarineViewItem> SubmarineViewItems
        {
            get => submarine_view_items;
            set => submarine_view_items = value;
        }
    }
}