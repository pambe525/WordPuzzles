from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from puzzles.forms import NewCrosswordForm


class HomeView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "home.html", {})



def get_grid_html(size):
    width = 31 * size
    grid_css = "style='width:" + str(width) + "px; height:" + str(width) + "px'"
    cell_css = "style='width:28px; height:28px;'"
    html = "<div class='xw-grid' " + grid_css + ">"
    for row in range(size+1):
        for col in range(size+1):
            class_name = "class='xw-cell'"
            if row == 0 and col != 0:
                class_name = "class='xw-header-top'"
            elif col == 0 and row != 0:
                class_name = "class='xw-header-left'"
            elif col == 0 and row == 0:
                class_name ="class='xw-corner'"
            html += "<div " + class_name + " " + cell_css + ">"
            if row == 0 and col > 0:
                html += "&#" + str(64+col)
            if col == 0 and row > 0:
                html += str(row)
            html += "</div>"
    html += '</div>'
    return html


class NewCrosswordView(LoginRequiredMixin, View):

    def get(self, request):
        form = NewCrosswordForm()
        #size = form.cleaned_data['size']
        grid_html = get_grid_html(13)
        return render(request, "new_xword.html", {'form': form, 'grid': grid_html})

    def post(self, request):
        form = NewCrosswordForm(request.POST)
        grid_html = ""
        if form.is_valid():
            size = form.cleaned_data['size']
            grid_html = get_grid_html(size)
        return render(request, "new_xword.html", {'form': form, 'grid': grid_html})


