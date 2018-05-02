using System.Collections.ObjectModel;

namespace user_interface_1_wpf
{
    class BatchesViewItem
    {
        private ObservableCollection<BatchViewItem> batch_value_view_items = new ObservableCollection<BatchViewItem>();

        public ObservableCollection<BatchViewItem> BatchViewItems
        {
            get => batch_value_view_items;
            set => batch_value_view_items = value;
        }
    }
}