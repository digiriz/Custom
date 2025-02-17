/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onWillRender, onMounted, useState } = owl
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class AttendanceDashboard extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.rpc = this.env.services.rpc;
        this.state = useState({
            employee_list: { value: [{}] },
            leave_summary : {},
            days: { value: 0 },
            user_name: { value: 'User Image' },
            user_img: { value: 'User Name' },
            requestData : {},
            rowsPerPage : 10,
            currentPage : 1,
        })
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
        await this.getUserDetail()
        await this.getGreetings()
        await loadJS("https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js")
    }

    async onMounted() {
        await this.renderAttendanceDashboardFilter();
        await this.getAttendanceData()
        this.getLeaveDetail({}, this.state.rowsPerPage, this.state.currentPage)
    }

    getUserDetail() {
        var self = this;
        jsonrpc('attn/user_detail').then(function (response) {
            self.state.user_name.value = response['user_name']
            self.state.user_img.value = response['user_img']
        });
    }

    getAttendanceData(requestData) {
        var self = this;
        const data = [];
        var request = {}
        if (requestData) {
            request = requestData;
            console.log(request);
        }
        jsonrpc('/employee/attendance', { 'request': request }).then(function (response) {
            self.state.employee_list.value = response[0]
            self.state.days.value = response[1].days
            self.prepareRoomCalender()
        })
    }

    getDayName(day, month, year) {
        console.log("called");
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const date = new Date(parseInt(year), parseInt(month), day);
        const dayIndex = date.getDay();
        const dayName = days[dayIndex];
        return dayName
    }


    async prepareRoomCalender() {
        // creating header 
        var self = this;
        var thead = document.querySelector("#attendanceCalender thead");
        thead.innerHTML = ' ';
        var tr = document.createElement('tr')
        var month = $('#month_selection').val()
        var year = $('#year_selection').val()

        // ; 
        // document.getElementById("month_selection");
        // var year = 2024
        // $('#year_selection').val();
        // const month = document.querySelector('#month_selection').value
        // const year = document.querySelector('#year_selection').value
        // const year = new Date().getFullYear();
        var days = self.state.days.value
        const employee_data = this.state.employee_list.value

        for (var i = 0; i <= days + 5; i++) {
            let th = document.createElement('th')
            if (i == 0) {
                th.style = "width:130px; background: #E0dfdf; border:1px solid #525252; text-align:center;  position: sticky; top: 0; z-index: 1;"
                th.textContent = "Employees"
            } else if (i == days + 1) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;P&nbsp;";
            } else if (i == days + 2) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;A&nbsp;";
            } else if (i == days + 3) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;L&nbsp;";
            } else if (i == days + 4) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0;z-index: 1;"
                th.innerHTML = "&nbsp;W&nbsp;";
            } else if (i == days + 5) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0;z-index: 1;"
                th.innerHTML = "&nbsp;H&nbsp;";
            } else {
                var day = this.getDayName(i, month, year)
                th.style = "background: #Eeeeee; height:35px; border:1px solid #525252; text-align:center;  position: sticky; top: 0;z-index: 1;"
                th.innerHTML = day + "<br>" + i;
            }
            tr.appendChild(th)
        }
        thead.appendChild(tr)

        // console.log(this.state.employee_list.value);

        // creating rows of table body
        var tbody = document.querySelector("#attendanceCalender tbody");
        tbody.innerHTML = ' ';

        for (var i = 0; i < employee_data.length; i++) {
            var tr = document.createElement('tr');
            tr.style = "height:50px;";
            for (var j = 0; j <= days + 5; j++) {
                var td = document.createElement('td');
                if (j === 0) {
                    td.style = "width:180px; border:1px solid #525252; padding-left:5px;";
                    if (employee_data[i]) {
                        var employee = employee_data[i];
                        // ${employee_data[i].img}
                        var emp = `<div class="row"> 
                                        <div class="col-3 d-flex my-auto ">
                                    `
                        if (employee_data[i].img) {
                            emp += `<img src="data:image/png;base64,${employee_data[i].img}" class="emp-img" alt="${employee_data[i].name} (Image)" />`
                        } else {
                            emp += `<img src="dev_attendance_dashboard_advanced/static/src/icons/emp.png" class="emp-img" />`
                        }

                        emp += ` </div> 
                                    <div class="col-9"> 
                                        <div class="row">
                                            <div class="col" style="font-weight:600;">${employee_data[i].name}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col">[${employee_data[i].job}]</div>
                                        </div>
                                    </div> 
                                </div>`

                        td.innerHTML = emp;
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.action.doAction({
                                    name: _t("Employee"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.employee',
                                    domain: [["id", "in", [employee.id]]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'current'
                                });
                            });
                        })(employee); // Pass room data to the IIFE
                    } else {
                        td.textContent = "-";
                    }
                    tr.appendChild(td);

                } else if (j === days + 1) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['p']
                    tr.appendChild(td);
                    if (employee.all_present) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.action.doAction({
                                    name: _t("Attendance"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.attendance',
                                    domain: [["id", "in", employee.all_present]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                } else if (j == days + 2) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['a']
                    tr.appendChild(td);
                } else if (j == days + 3) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['l']
                    tr.appendChild(td);
                    var employee = employee_data[i];
                    if (employee.all_leave) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.action.doAction({
                                    name: _t("Leaves"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.leave',
                                    domain: [["id", "in", employee.all_leave]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                } else if (j == days + 4) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['w']
                    tr.appendChild(td);
                } else if (j == days + 5) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['h']
                    tr.appendChild(td);
                    var employee = employee_data[i];
                    if (employee.all_holidays) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.action.doAction({
                                    name: _t("Holidays"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'resource.calendar.leaves',
                                    domain: [["id", "in", employee.all_holidays]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                }
                else {
                    if (employee_data[i].attendance) {
                        var attendance = employee_data[i].attendance
                        var employee = employee_data[i]
                        if (attendance[j].status === 'absent') {
                            td.style = "text-align:center; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "A"
                        } else if (attendance[j].status == 'W') {
                            td.style = "text-align:center; font-weight:600; background-color: #Eeeeee; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "W"
                        } else if (attendance[j].status === 'l') {
                            td.style = "text-align:center; font-weight:600; color:red; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "L";
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.action.doAction({
                                        name: _t("Leave"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'hr.leave',
                                        domain: [["id", "in", [day_attn.ids]]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        } else if (attendance[j].status === 'holiday') {
                            td.style = "text-align:center; font-weight:600; color:Blue; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "H";
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.action.doAction({
                                        name: _t("Holidays"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'resource.calendar.leaves',
                                        domain: [["id", "in", [day_attn.ids]]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        } else {
                            td.style = "text-align:center; font-weight:600; color:green; font-size:13px;  border-bottom:1px #525252 solid;";
                            td.textContent = attendance[j].hours + ' H';
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.action.doAction({
                                        name: _t("Attendance"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'hr.attendance',
                                        domain: [["id", "in", day_attn.ids]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        }
                    } else {
                        td.textContent = "A";
                    }
                    tr.appendChild(td);
                }
            }
            tbody.appendChild(tr);
        }
    }

    // var day = attendance[k].booking_date.split('-')[2]

    //             // var booking_id = bookingDetail[k].booking_id
    //             // if (day == j) {
    //             //     td.textContent = "BO";
    //             //     td.style = "border:1px solid #d6d6d6; background:rgba(255, 0, 56, 0.4); text-align:center;font-weight:600;";
    //             //     (function (booking_id) {
    //             //         td.addEventListener("click", function () {
    //             //             self.action.doAction({
    //             //                 name: _t("Booking"),
    //             //                 type: 'ir.actions.act_window',
    //             //                 res_model: 'dev.book.hotel',
    //             //                 domain: [["id", "in", [booking_id]]],
    //             //                 view_mode: 'tree,form',
    //             //                 views: [
    //             //                     [false, 'tree'],
    //             //                     [false, 'form']
    //             //                 ],
    //             //                 target: 'current'
    //             //             });
    //             //         });
    //             //     })(booking_id);
    //             //     break;
    //             // } else {
    //             //     td.textContent = "NB";
    //             // }

    async getGreetings() {
        var self = this;
        const now = new Date();
        const hours = now.getHours();
        if (hours >= 5 && hours < 12) {
            self.greetings = "Good Morning";
        }
        else if (hours >= 12 && hours < 18) {
            self.greetings = "Good Afternoon";
        }
        else {
            self.greetings = "Good Evening";
        }
    }

    downloadReport(e) {
        e.stopPropagation();
        e.preventDefault();

        var opt = {
            margin: 1,
            filename: 'AttendanceDashboard.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'px', format: [1920, 1080], orientation: 'landscape' }
        };
        html2pdf().set(opt).from(document.getElementById("dashboard")).save()

    }

    createCheckIn(e) {
        e.stopPropagation();
        e.preventDefault();
        var self = this;

        self.action.doAction({
            name: _t("Check In"),
            type: 'ir.actions.act_window',
            res_model: 'check_in.check_in',
            domain: [],
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }

    createBooking(e) {
        e.stopPropagation();
        e.preventDefault();
        var self = this;

        self.action.doAction({
            name: _t("Booking"),
            type: 'ir.actions.act_window',
            res_model: 'dev.book.hotel',
            domain: [],
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }


    renderAttendanceDashboardFilter() {
        jsonrpc('/render_attendance_dashboard_filter').then(function (data) {
            var employees = data[0]
            var departments = data[1]
            console.log(document.getElementById('month_selection'))
            console.log($('#employee_selection'), $('#department_selection'), $('#month_selection'));
            $(employees).each(function (employee) {
                $('#employee_selection').append("<option value=" + employees[employee].id + ">" + employees[employee].name + "</option>");
            });

            $(departments).each(function (department) {
                $('#department_selection').append("<option value=" + departments[department].id + ">" + departments[department].name + "</option>");
            });

            const date = new Date();
            const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            for (var i = 0; i < monthNames.length; i++) {
                if (i == date.getMonth()) {
                    $('#month_selection').append("<option value=" + i + " selected >" + monthNames[i] + "</option>");
                } else {
                    $('#month_selection').append("<option value=" + i + ">" + monthNames[i] + "</option>");
                }
            }

            for (var i = 0; i <= 5; i++) {
                var year = date.getFullYear() - i
                if (year == date.getFullYear()) {
                    $('#year_selection').append("<option value=" + year + " selected >" + year + "</option>");
                } else {
                    $('#year_selection').append("<option value=" + year + ">" + year + "</option>");
                }
            }
        })
    }

    _onchangeAttendanceFilter(ev) {
        var employee_selection = $('#employee_selection').val();
        var department_selection = $('#department_selection').val();
        var month_selection = $('#month_selection').val();
        var year_selection = $('#year_selection').val();
        const requestData = { 'employee': employee_selection, 'department': department_selection, 'month': month_selection, 'year': year_selection }
        this.getAttendanceData(requestData)
        this.state.requestData = requestData
        this.getLeaveDetail(this.state.requestData, this.state.rowsPerPage, this.state.currentPage)
        console.log("mmmmm",this.state.rowsPerPage, this.state.currentPage);
        
    }

    getLeaveDetail(requestData, rowsPerPage, currentPage) {
        var self = this;
        console.log("called", requestData, rowsPerPage, currentPage);
        
        jsonrpc('/employee/leave', { 'request': requestData }).then(function (response) {
            var tbody = document.querySelector("#leaveDetail tbody");
            tbody.innerHTML = ' ';
            console.log(response);
            console.log(self.state.leave_summary);
            
            
            self.state.leave_summary = response
            console.log(self.state.leave_summary);

            // self.state.all_applicant_list_length = self.state.all_applicant_list.length
            
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            console.log(start, end);
            
            const paginatedData =  self.state.leave_summary.slice(start, end)
            console.log("paginatedData",paginatedData);

            for (var i = 0; i <= paginatedData.length; i++) {
                var tr = document.createElement('tr');
                const newBtn = document.createElement('button');
                newBtn.textContent = 'View';
                newBtn.style = "background-color: #71639e; color: white;";
                newBtn.className = "btn btn-primary";
                for (var key in paginatedData[i]) {
                    if (key === 'id') {
                        newBtn.value = paginatedData[i][key];
                    } else {
                        let td = document.createElement('td');
                        if (paginatedData[i][key].length === 2) {
                            td.textContent = paginatedData[i][key][1];
                            tr.appendChild(td);
                        } else if (paginatedData[i][key] === false) {
                            td.textContent = '-';
                            tr.appendChild(td);
                        } else {
                            td.textContent = paginatedData[i][key];
                            tr.appendChild(td);
                        }
                        if (key === 'name') {
                            var btnCell = document.createElement('td');
                            tr.appendChild(btnCell);
                            btnCell.appendChild(newBtn)
                        }
                    }
                }
                tbody.appendChild(tr);
                newBtn.addEventListener('click', function () {
                    viewLeave(newBtn.value);
                });
            }
        })

        function viewLeave(id) {
            var options = {
            };
            self.action.doAction({
                name: _t("Leave"),
                type: 'ir.actions.act_window',
                res_model: 'hr.leave',
                res_id: parseInt(id),
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new'
            }, options)
        }
    }

    prevPage(e) {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
            this.getLeaveDetail(this.state.requestData, this.state.rowsPerPage, this.state.currentPage);
            document.getElementById("next_button").disabled = false;
        }
        if (this.state.currentPage == 1) {
            document.getElementById("prev_button").disabled = true;
        } else {
            document.getElementById("prev_button").disabled = false;
        }
    }

    nextPage() {
        if ((this.state.currentPage * this.state.rowsPerPage) < this.state.leave_summary.length) {
            this.state.currentPage++;
            this.getLeaveDetail(this.state.requestData, this.state.rowsPerPage, this.state.currentPage);
            document.getElementById("prev_button").disabled = false;
        }
        if (Math.ceil(this.state.leave_summary / this.state.rowsPerPage) == this.state.currentPage) {
            document.getElementById("next_button").disabled = true;
        } else {
            document.getElementById("next_button").disabled = false;
        }
    }


    /**
     * Event handler to open a list of projects and display them to the user.
     */

    // _downloadChart(e) {
    //     console.log("download called !!!!", e.target.offsetParent.children[1].children[0]);
    //     // console.log("download called !!!!", document.querySelector("#all_order_chart_data"));
    //     const chart = e.target.offsetParent.children[1].children[0]; // Get the chart canvas element
    //     const imageDataURL = chart.toDataURL('image/png'); // Generate image data URL
    //     const filename = chart.id+'.png'; // Set your preferred filename
    //     const link = document.createElement('a');
    //     link.href = imageDataURL;
    //     link.download = filename;
    //     link.click();
    // }

}
AttendanceDashboard.template = "AttendanceDashboard"
registry.category("actions").add("attendance_dashboard", AttendanceDashboard)
