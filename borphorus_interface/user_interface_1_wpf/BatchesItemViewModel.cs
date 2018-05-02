using System.Collections.ObjectModel;

namespace user_interface_1_wpf
{
    class BatchesItemViewModel
    {
        private ObservableCollection<BatchesViewItem> batches_view_items = new ObservableCollection<BatchesViewItem>();

        public ObservableCollection<BatchesViewItem> BatchesViewItems
        {
            get => batches_view_items;
            set => batches_view_items = value;
        }
    }
}