from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import datetime

class GraphUtils:
    @staticmethod
    def add_sunday_markers(ax, dates):
        """Adds a vertical dashed line for every Sunday in the date range."""
        if not dates:
            return
            
        import matplotlib.dates as mdates
        
        # Determine if dates are datetimes or floats
        test_date = dates[0]
        if isinstance(test_date, datetime.datetime) or isinstance(test_date, datetime.date):
            start_date = min(dates)
            end_date = max(dates)
        else:
            # Assume floats
            start_date = mdates.num2date(min(dates))
            end_date = mdates.num2date(max(dates))
        
        # Align start to next Sunday
        # start_date.weekday(): Mon=0, Sun=6
        days_to_sunday = (6 - start_date.weekday()) % 7
        current_sunday = start_date + datetime.timedelta(days=days_to_sunday)
        
        # Ensure we don't start before the start_date due to time components?
        # Actually logic is fine.
        
        while current_sunday <= end_date:
            # Draw line
            m_date_float = mdates.date2num(current_sunday)
            ax.axvline(x=m_date_float, color='gray', linestyle='--', alpha=0.3, linewidth=1)
            
            # Next Sunday
            current_sunday += datetime.timedelta(days=7)

    @staticmethod
    def enable_zoom(fig, canvas, ax):
        """Enables mouse wheel zoom on the x-axis."""
        def zoom(event):
            a = ax
            if event.inaxes != a:
                return
            
            # Zoom scale
            scale_factor = 1.1
            if event.button == 'up':
                scale_factor = 1 / scale_factor
            elif event.button == 'down':
                scale_factor = scale_factor
            else:
                return

            cur_xlim = a.get_xlim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])
            xdata = event.xdata # get event x location
            
            new_width = cur_xrange * scale_factor
            new_left = xdata - new_width * (xdata - cur_xlim[0]) / cur_xrange
            new_right = new_left + new_width
            
            a.set_xlim([new_left, new_right])
            canvas.draw_idle()

        # Bind scroll event
        # 'scroll_event' works for most backends
        canvas.mpl_connect('scroll_event', zoom)

    @staticmethod
    def add_toolbar(canvas, parent_frame, pack_side="bottom"):
        """Adds the standard matplotlib toolbar."""
        toolbar = NavigationToolbar2Tk(canvas, parent_frame)
        toolbar.update()
        toolbar.pack(side=pack_side, fill="x")
        return toolbar
